from __future__ import annotations

import unittest
from hezqen_gpu_planner import HardwareProfile, ModelProfile, PlanningError, estimate


def model():
    return ModelProfile("org/example-70b",70,80,8,128,32768)


def hw(**overrides):
    values={"gpus_per_node":4,"nodes":1,"vram_gib_per_gpu":24,"tensor_parallel_size":4,"pipeline_parallel_size":1,"max_model_len":8192,"max_num_seqs":8,"weight_dtype":"int4","kv_cache_dtype":"fp16"}
    values.update(overrides)
    return HardwareProfile(**values)


class PlannerTests(unittest.TestCase):
    def test_70b_int4_four_24gb_gpus_estimate(self):
        plan=estimate(model(),hw())
        self.assertTrue(plan.memory["estimated_fit"])
        self.assertGreater(plan.memory["weights_gib_per_gpu"],8)
        self.assertGreater(plan.memory["kv_cache_gib_per_gpu"],0)
        self.assertIn("--tensor-parallel-size 4",plan.vllm["shell_command"])

    def test_kv_memory_scales_with_context_and_concurrency(self):
        small=estimate(model(),hw())
        large=estimate(model(),hw(max_model_len=16384,max_num_seqs=16))
        self.assertGreater(large.memory["kv_cache_gib_per_gpu"],small.memory["kv_cache_gib_per_gpu"])

    def test_pipeline_parallelism_reduces_per_gpu_memory(self):
        single=estimate(model(),hw(nodes=2,gpus_per_node=4))
        pipelined=estimate(model(),hw(nodes=2,gpus_per_node=4,pipeline_parallel_size=2))
        self.assertLess(pipelined.memory["weights_gib_per_gpu"],single.memory["weights_gib_per_gpu"])
        self.assertLess(pipelined.memory["kv_cache_gib_per_gpu"],single.memory["kv_cache_gib_per_gpu"])

    def test_rejects_context_over_model_limit(self):
        with self.assertRaisesRegex(PlanningError,"context limit"):
            estimate(model(),hw(max_model_len=65536))

    def test_rejects_tp_over_gpus_per_node(self):
        with self.assertRaisesRegex(PlanningError,"GPUs per node"):
            estimate(model(),hw(nodes=2,tensor_parallel_size=8))

    def test_rejects_pp_over_node_count(self):
        with self.assertRaisesRegex(PlanningError,"node count"):
            estimate(model(),hw(pipeline_parallel_size=2))

    def test_rejects_invalid_memory_utilization(self):
        with self.assertRaisesRegex(PlanningError,"gpu_memory_utilization"):
            estimate(model(),hw(gpu_memory_utilization=1.0))

    def test_reports_non_fit_for_small_gpu(self):
        plan=estimate(model(),hw(vram_gib_per_gpu=8))
        self.assertFalse(plan.memory["estimated_fit"])
        self.assertTrue(any("exceeds" in warning for warning in plan.warnings))

    def test_plan_contains_command(self):
        plan=estimate(model(),hw(weight_dtype="bf16"))
        self.assertEqual(plan.to_dict()["model"]["name"],"org/example-70b")
        self.assertEqual(plan.command()[0],"vllm")


if __name__ == "__main__":
    unittest.main()
