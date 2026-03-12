<template>
  <div class="layout">
    <header class="header">
      <h1>Magic Partner</h1>
      <nav>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/images">图片库</RouterLink>
      </nav>
    </header>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>
