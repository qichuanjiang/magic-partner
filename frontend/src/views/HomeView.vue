<template>
  <section class="card home-hero">
    <div class="home-copy">
      <p class="eyebrow">Magic Partner</p>
      <h2 class="page-title">欢迎来到图片素材库</h2>
      <p class="muted">
        这里用于收集、整理和保存项目素材图片。你可以从这里进入图片库，上传新图片，或者查看已经保存的内容。
      </p>
    </div>

    <div class="home-actions">
      <RouterLink to="/images" class="hero-link primary-link">上传图片</RouterLink>
      <RouterLink to="/images" class="hero-link secondary-link">查看图片库</RouterLink>
    </div>

    <div class="home-notes">
      <div class="note-card">
        <h3>批量上传</h3>
        <p>支持一次上传多张图片，并按图片简称归档到同一个目录。</p>
      </div>
      <div class="note-card">
        <h3>即时管理</h3>
        <p>上传后可直接查看缩略图、删除单图或删除整个文件夹。</p>
      </div>
    </div>
  </section>
</template>
