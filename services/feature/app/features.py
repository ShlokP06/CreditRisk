import asyncio
import math
from datetime import timedelta

import networkx as nx

from .schemas import SubgraphPayload


class RunningStats:
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0

    def update(self, x):
        self.count += 1
        delta = x - self.mean
        self.mean += delta / self.count
        delta2 = x - self.mean
        self.m2 += delta * delta2

    def normalize(self, x):
        if self.count < 2:
            return 0.0
        std = math.sqrt(self.m2 / self.count)
        return (x - self.mean) / (std + 1e-8)


class FeatureEngine:
    def __init__(self):
        self.user_history = {}
        self.merchant_history = {}
        self.graph = nx.Graph()
        self.amount_stats = RunningStats()
        self.lock = asyncio.Lock()

    async def extract(self, txn):
        async with self.lock:
            ts = txn.timestamp
            self.prune(self.user_history, ts)
            self.prune(self.merchant_history, ts)

            self.graph.add_edge(txn.user_id, txn.merchant_id)
            self.amount_stats.update(txn.amount)

            node_count = max(self.graph.number_of_nodes(), 1)
            user_degree = self.graph.degree(txn.user_id)
            merchant_degree = self.graph.degree(txn.merchant_id)

            user_vel_1h = self.velocity(self.user_history, txn.user_id, ts, 1)
            user_vel_24h = self.velocity(self.user_history, txn.user_id, ts, 24)
            merchant_vel_1h = self.velocity(self.merchant_history, txn.merchant_id, ts, 1)
            merchant_vel_24h = self.velocity(self.merchant_history, txn.merchant_id, ts, 24)

            amount_norm = self.amount_stats.normalize(txn.amount)

            user_features = [
                user_degree / node_count,
                user_vel_1h / 10.0,
                user_vel_24h / 100.0,
                amount_norm,
            ]
            merchant_features = [
                merchant_degree / node_count,
                merchant_vel_1h / 10.0,
                merchant_vel_24h / 100.0,
                amount_norm,
            ]
            edge_features = [
                amount_norm,
                ts.hour / 23.0,
                float(ts.weekday() >= 5),
            ]

            self.user_history.setdefault(txn.user_id, []).append((ts, txn.amount))
            self.merchant_history.setdefault(txn.merchant_id, []).append((ts, txn.amount))

            return SubgraphPayload(
                transaction_id=txn.transaction_id,
                user_id=txn.user_id,
                user_features=user_features,
                merchant_features=merchant_features,
                edge_features=edge_features,
            )

    def velocity(self, history, node_id, ts, hours):
        cutoff = ts - timedelta(hours=hours)
        return sum(1 for t, _ in history.get(node_id, []) if t >= cutoff)

    def prune(self, history, ts):
        cutoff = ts - timedelta(hours=24)
        for node_id in list(history.keys()):
            kept = [(t, a) for t, a in history[node_id] if t >= cutoff]
            if kept:
                history[node_id] = kept
            else:
                del history[node_id]
