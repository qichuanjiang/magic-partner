<template>
  <div class="layout">
    <header class="header">
      <h1>Fullstack Starter</h1>
      <nav>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/about">关于</RouterLink>
      </nav>
    </header>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
