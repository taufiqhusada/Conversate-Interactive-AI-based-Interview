<template>
  <div>
    <audio controls class="audioPlayer shadow" ref="audioPlayerRef" @timeupdate="updateSeekTime">
      <source :src="audioUrl" type="audio/mpeg" />
    </audio>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, onMounted, watch } from 'vue';

export default defineComponent({
  props: {
    audioUrl: {
      type: String,
    },
    clickedTranscriptTime: {
      type: Number,
    },
  },
  setup(props, context) {
    const audioPlayerRef = ref<HTMLAudioElement | null>(null);
    const prevSeekTime = ref<number>(0);

    const updateSeekTime = () => {
      if (audioPlayerRef.value) {
        const currentTime = audioPlayerRef.value.currentTime;
        if (Math.abs(currentTime - prevSeekTime.value) >= 0.1) {
          prevSeekTime.value = currentTime;
          context.emit('video-seek-time-updated', currentTime);
        }
      }
    };

    const Init = () => {
      // Your Init logic remains the same
    };

    watch(() => props.clickedTranscriptTime, () => {
      if (audioPlayerRef.value && typeof props.clickedTranscriptTime === 'number') {
        audioPlayerRef.value.currentTime = props.clickedTranscriptTime;
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
      audioPlayerRef,
    };
  }
});
</script>

<style scoped>
.audioPlayer {
    /* width: 66%;
    height: auto; */
    padding: 20px;
    border-radius: 5px;
    background-color: #eee;
    color: #444;
    margin: 20px auto;
    overflow: hidden;
    
}
audio {
  width:100%;
}
audio:nth-child(2), audio:nth-child(4), audio:nth-child(6) {
    margin: 0;
}
</style>
