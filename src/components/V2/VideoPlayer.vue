<template>
  <div>
    <audio hidden controls class="audioPlayer shadow" ref="audioPlayerRef" @timeupdate="updateSeekTime">
      <source :src="audioUrl" type="audio/mpeg" />
    </audio>
    <div class="audioPlayerContainer mt-3">
      <div class="controls">
        <button @click="togglePlay" class="playPause">{{ isPlaying ? '⏸' : '▶️' }}</button>
        <span class="time">{{ currentTimeFormatted }} / {{ durationFormatted }}</span>
      </div>
      <div class="seekBar" ref="seekBarRef" @click="seekAudio($event)" @mousedown="startDrag" @mousemove="dragging" @mouseup="endDrag">
        <div class="progress" :style="{ width: progress + '%'}"></div>
        <!-- Timestamp marks --> 
        <div v-show="isShowingMoments" v-for="(data, index) in identifiedMoments" :key="index"
             class="timestampMark"
             :style="{ left: calculateTimestampPosition(data['timeOffset_start']) + '%', 
                       width: calculateTimestampWidth(data['timeOffset_start'],data['timeOffset_end']) + '%' }"></div>

        <div v-for="(data, index) in pinnedMoments" :key="index"
             class="arrow-right"
             :style="{ left: calculateTimestampPosition(data[0]) + '%'}"></div>

        <div v-for="(data, index) in pinnedMoments" :key="index"
             class="arrow-left"
             :style="{ left: calculateTimestampPosition(data[1]) + '%'}"></div>

        <div v-if="pinnedStart" class="arrow-right"
             :style="{ left: calculateTimestampPosition(pinnedStart) + '%'}"></div>

        <div v-if="pinnedEnd" class="arrow-left"
             :style="{ left: calculateTimestampPosition(pinnedEnd) + '%'}"></div>

        <div v-if="currentTime" class="rectangle"
             :style="{ left: calculateTimestampPosition(currentTime) - 0.2 + '%'}"></div>

      </div>
      <button v-show="!isShowingMoments" class="btn btn-outline-primary" @click="showSuggestedMoments" style="margin-left: 19px;">  Show Suggested Moments</button>
      <button v-show="isShowingMoments" class="btn btn-outline-primary" @click="unShowSuggestedMoments">Unshow Suggested Moments</button>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, defineComponent, onMounted, watch, computed } from 'vue';


interface IdentifiedMoment {
  quality: string;
  timeOffset_start: number;
  timeOffset_end: number;
}


export default defineComponent({
  props: {
    audioUrl: {
      type: String,
    },
    clickedTranscriptTime: {
      type: Number,
    },
    // suggestedTimestamps: {
    //   type: Array as () => Array<[number, number]>,
    //   default: () => {
    //     // Example: Array of timestamp pairs (start, end) in seconds
    //     return [
    //       [1, 2],
    //       [4, 5],
    //     ];
    //   }
    // },
    identifiedMoments: {
      type: Array as () => Array<IdentifiedMoment>
    },
    pinnedMoments: {
      type: Array as () => Array<[number, number]>,
    },
    pinnedStart: {
      type: Number
    },
    pinnedEnd: {
      type: Number
    },
  },
  setup(props, context) {
    const prevSeekTime = ref<number>(0);
    const audioPlayerRef = ref(new Audio(props.audioUrl));
    const isPlaying = ref(false);
    const progress = ref(0);
    const duration = ref(0);
    const currentTime = ref(0);
    const seekBarWidth = ref(0);
    const isDragging = ref(false);
    const isShowingMoments = ref(false);

    const updateSeekTime = () => {
      if (audioPlayerRef.value) {
        const currentTime = audioPlayerRef.value.currentTime;
        if (Math.abs(currentTime - prevSeekTime.value) >= 0.1) {
          prevSeekTime.value = currentTime;
          context.emit('video-seek-time-updated', currentTime);
        }
      }
    };

    const seekBarRef = ref<HTMLDivElement | null>(null);

    const calculateTimestampPosition = (timestamp: number) => {
      if (duration.value > 0) {
        console.log(duration.value)
        return (timestamp / duration.value) * 100; // Use the reactive duration
      }
      return 0;
    };

    const calculateTimestampWidth = (start: number, end: number) => {
      const segmentDuration = end - start;
      return (segmentDuration / duration.value) * 100;
    };


    const Init = () => {
      // Your Init logic remains the same
    };

    watch(() => props.clickedTranscriptTime, () => {
      if (audioPlayerRef.value && typeof props.clickedTranscriptTime === 'number') {
        audioPlayerRef.value.currentTime = props.clickedTranscriptTime;
      }
    });

    const currentTimeFormatted = computed(() => {
      return new Date(currentTime.value * 1000).toISOString().substr(14, 5);
    });

    const durationFormatted = computed(() => {
      return new Date(duration.value * 1000).toISOString().substr(14, 5);
    });

    const togglePlay = () => {
      if (!isPlaying.value) {
        audioPlayerRef.value.play();
        isPlaying.value = true;
      } else {
        audioPlayerRef.value.pause();
        isPlaying.value = false;
      }
    };

    const seekAudio = (event: MouseEvent) => {
      const seekBar = event.target as HTMLElement;
      const clickX = event.offsetX;

      seekBarWidth.value = seekBarWidth.value || seekBar.offsetWidth

      // change seek position
      progress.value = (clickX / seekBarWidth.value) * 100
      const percentage = clickX / seekBarWidth.value;

      const newTime = percentage * duration.value;

      console.log(clickX, seekBarWidth.value, percentage, duration.value, newTime)
      audioPlayerRef.value.currentTime = newTime;
    };

    const updateSeekBarWidth = (e: Event) => {
      // Assuming that you want to update the progress bar width when window resizes.
      // This function should contain the logic to update the progress bar's width.
      // You may need to recalculate the positions of your timestamp marks here.
      let prog = this
      setTimeout(()=>{
        const seekBar = e.target as HTMLElement;
        seekBarWidth.value = seekBar.offsetWidth
      }, 200)
    };


    const startDrag = (event: MouseEvent) => {
      isDragging.value = true;
      seekAudio(event);
    };

    const dragging = (event: MouseEvent) => {
      if (isDragging.value ) {
        seekAudio(event);
      }
    };

    const endDrag = () => {
      isDragging.value = false;
    };

    const showSuggestedMoments = () => {
      isShowingMoments.value = true;
      context.emit('show-suggested-moments', true);
    }

    const unShowSuggestedMoments = () => {
      isShowingMoments.value = false;
      context.emit('show-suggested-moments', false);
    }

    onMounted(() => {
      audioPlayerRef.value.addEventListener('loadedmetadata', () => {
        duration.value = audioPlayerRef.value.duration;
      });

      audioPlayerRef.value.addEventListener('timeupdate', () => {
        currentTime.value = audioPlayerRef.value.currentTime;
        progress.value = (currentTime.value / duration.value) * 100;
      });

      audioPlayerRef.value.addEventListener('ended', () => {
        isPlaying.value = false;
        // progress.value = 0;
      });

      //add a listener that will listen to window resize and modify progress width accordingly
      window.addEventListener('resize', updateSeekBarWidth, false)
    });

    return {
      Init,
      updateSeekTime,
      audioPlayerRef,
      calculateTimestampPosition,
      seekBarRef,
      duration,
      seekAudio,
      progress,
      togglePlay,
      isPlaying,
      currentTimeFormatted,
      durationFormatted,
      calculateTimestampWidth,
      currentTime,
      startDrag,
      dragging,
      endDrag,
      isShowingMoments,
      showSuggestedMoments,
      unShowSuggestedMoments
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
  width: 100%;
}

audio:nth-child(2),
audio:nth-child(4),
audio:nth-child(6) {
  margin: 0;
}

.audioPlayerContainer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px;
  background-color: #fff;
  /* box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2); */
  box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  width: 100%;
  box-sizing: border-box;
}

.controls {
  display: flex;
  align-items: center;
}

.playPause,
.volume,
.more {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
}

.time {
  margin: 0 10px;
  font-size: 14px;
}

.seekBar {
  flex-grow: 1;
  height: 7px;
  background-color: #ddd;
  border-radius: 5px;
  cursor: pointer;
  position: relative;
  margin: 0 10px;
}

.progress {
  height: 100%;
  background-color: #000;
  border-radius: 5px;
  width: 0;
  /* This width will be dynamically updated based on audio progress */
}

.playPause {
  background: none;
  border: none;
  cursor: pointer;
  /* Add styles for a bigger button if needed */
}

.timestampMark {
  position: absolute;
  bottom: 0;
  height: 100%;
  background-color: orange;
  border-radius: 5px;
  pointer-events: none;
  /* Optional: to match the seek bar's rounded corners */
}

.arrow-right {
  position: absolute;
  bottom: -7px;
  height: 100%;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  
  border-left: 7px solid green;
  pointer-events: none;
}

.arrow-left {
  position: absolute;
  bottom: -7px;
  height: 100%;
  border-top: 10px solid transparent;
  border-bottom: 10px solid transparent;
  
  border-right: 7px solid green;
  pointer-events: none;
}

.rectangle {
  position: absolute;
  bottom: -7px;
  height: 21px;
  border-right: 4px solid blue;
  pointer-events: none;
}
</style>
