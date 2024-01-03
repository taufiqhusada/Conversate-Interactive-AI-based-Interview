import { type RouteRecordRaw, createRouter, createWebHistory } from 'vue-router';
import VideoRecorder from '@/views/VideoRecorder.vue'; // Replace this with your correct path
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;