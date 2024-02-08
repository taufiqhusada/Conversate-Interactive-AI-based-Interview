import { type RouteRecordRaw, createRouter, createWebHistory } from 'vue-router';
import VideoRecorder from '@/views/VideoRecorder.vue'; // Replace this with your correct path
import Reflection from '@/views/Reflection.vue'; // Replace this with your correct path
import Main from '@/views/Main.vue';

const routes = [
  {
    path: '/uploader',
    name: 'Main',
    component: Main,
  }, {
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