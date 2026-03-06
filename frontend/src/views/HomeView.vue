<template>
  <section class="card">
    <h2>首页</h2>

    <div class="row">
      <label for="name">姓名：</label>
      <input id="name" v-model="name" placeholder="输入你的名字" />
      <button type="button" @click="loadGreeting">调用后端接口</button>
    </div>

    <p v-if="health" class="ok">后端状态：{{ health.status }}</p>
    <p v-if="greeting">返回消息：{{ greeting.message }}</p>

    <div class="row">
      <button type="button" @click="counter.increment">Pinia 计数 +1</button>
      <span>当前计数：{{ counter.count }}</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchGreeting, fetchHealth, type GreetingResponse } from '@/api/demo'
import { useCounterStore } from '@/stores/counter'

const name = ref('SpringBoot')
const health = ref<{ status: string } | null>(null)
const greeting = ref<GreetingResponse | null>(null)
const counter = useCounterStore()

const loadHealth = async () => {
  health.value = await fetchHealth()
}

const loadGreeting = async () => {
  greeting.value = await fetchGreeting(name.value || 'World')
}

onMounted(async () => {
  await loadHealth()
})
</script>
