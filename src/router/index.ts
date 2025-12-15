import { type RouteRecordRaw, createRouter, createWebHistory } from 'vue-router';
import VideoRecorder from '@/views/VideoRecorder.vue';
import Reflection from '@/views/Reflection.vue';

const routes = [
  {
    path: '/',
    name: 'VideoRecorder',
    component: VideoRecorder,
  },
  {
    path: '/reflection',
    name: 'Reflection',
    component: Reflection,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;