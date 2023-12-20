<template>
  <div>
    <video controls class="videoPlayer mt-4" ref="videoPlayerRef" @timeupdate="updateSeekTime">
      <source :src="videoUrl" type="video/mp4" />
    </video>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, onMounted, watch } from 'vue';

export default defineComponent({
  props: {
    videoUrl: {
      type: String,
    },
    clickedTranscriptTime: {
      type: Number,
    },
  },
  setup(props, context) {
    const videoPlayerRef = ref<HTMLVideoElement | null>(null);
    const prevVideoSeekTime = ref<number>(0);

    const updateSeekTime = () => {
      if (videoPlayerRef.value) {
        const currentTime = videoPlayerRef.value.currentTime;
        if (Math.abs(currentTime - prevVideoSeekTime.value) >= 0.1) {
          prevVideoSeekTime.value = currentTime;
          context.emit('video-seek-time-updated', currentTime);
        }
      }
    };

    const Init = () => {
      // Your Init logic remains the same
    };

    watch(() => props.clickedTranscriptTime, () => {
      if (videoPlayerRef.value && typeof props.clickedTranscriptTime === 'number') {
        videoPlayerRef.value.currentTime = props.clickedTranscriptTime;
      }
    });

    onMounted(() => {
      if (window.File && window.FileList && window.FileReader) {
        Init();
      } else {
        const fileDrag = document.getElementById('file-drag') as HTMLElement;
        if (fileDrag) {
          fileDrag.style.display = 'none';
        }
      }
    });

    return {
      Init,
      updateSeekTime,
      videoPlayerRef,
    };
  }
});
</script>

<style scoped>
.videoPlayer {
  width: 100%;
  height: auto;
  max-width: 100%;
  max-height: 15rem;
}
</style>
