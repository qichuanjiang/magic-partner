import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ImageFolderView from '@/views/image-library/ImageFolderView.vue'
import ImageLibraryView from '@/views/image-library/ImageLibraryView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/images', name: 'image-library', component: ImageLibraryView },
    { path: '/images/:slug', name: 'image-folder', component: ImageFolderView }
  ]
})

export default router
