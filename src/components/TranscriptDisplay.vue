<template>
  <div v-if="transcript.length !== 0">
    <section ref="chatArea" class="chat-area">
      <h4 class="headline">Transcript</h4>
      <div v-for="(message, index) in transcript" :key="index" :class="[messageHighlight(message), { 'margin-right': message.speaker === 'assistant', 'margin-left': message.speaker === 'user'}]" @click="handleTranscriptClick(message)" type="button" >
        <div class="message-container">
          <div class="content">
            <span :class="[{'speaker-1': message.speaker === 'Speaker 1' || message.speaker === 'user', 'speaker-2': message.speaker === 'Speaker 2' || message.speaker === 'assistant'}]">
              <b>{{ message.speaker }}:</b>
            </span> 
            {{ message.text }}
          </div>
          <div class="time" :class="{ 'highlight-time': isTimeInIdentifiedMoment(message.timeOffset) && isShowingMoments }"><b>{{ convertTimeToHHMMSS(message.timeOffset) }}</b></div>
        </div>
      </div>
    </section>
  </div>
</template>


<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

interface TranscriptMessage {
  text: string;
  timeOffset: number;
  speaker: string;
}

interface IdentifiedMoment {
  quality: string;
  timeOffset_start: number;
  timeOffset_end: number;
}

export default defineComponent({
  props: {
    transcript: {
      type: Array as () => Array<TranscriptMessage>,
      required: true,
    },
    timestampHighlights: {
      type: Array as () => Array<[number, number]>,
      required: true,
    },
    currentVideoSeekTime: {
      type: Number,
      required: false
    },
    identifiedMoments: {
      type: Array as () => Array<IdentifiedMoment>
    },
    isShowingMoments : {
      type: Boolean,
      required: true
    }
  },
  methods: {
    convertTimeToHHMMSS(timeOffset: number): string {
      const date = new Date(timeOffset * 1000);
      const hours = date.getUTCHours();
      const minutes = date.getUTCMinutes();
      const seconds = date.getUTCSeconds();

      // Display format as hh:mm:ss
      return (
        (hours < 10 ? '0' : '') + hours + ':' +
        (minutes < 10 ? '0' : '') + minutes + ':' +
        (seconds < 10 ? '0' : '') + seconds
      );
    },
  },
  setup(props, context) {
    const chatArea = ref<HTMLElement | null>(null);
    let highlightedIndex = -1;

    const messageHighlight = (message: TranscriptMessage) => {
      return isInHighlightedRange(message.timeOffset) ? 'btn message message-in highlight' : 'btn message message-in';
    };

    const isInHighlightedRange = (timeOffset: number) => {
      return props.timestampHighlights.some(([start, end]) => timeOffset >= start && timeOffset <= end);
    };

    watch(() => props.timestampHighlights, () => {
      applyHighlightingBasedOnSelection();
    });

    const applyHighlightingBasedOnSelection = () => {
      const area = chatArea.value;
      if (area && props.transcript.length > 0) {
        const messages = area.querySelectorAll('.message') as NodeListOf<HTMLElement>;
        let scrolled = false;

        messages.forEach((message: HTMLElement, index: number) => {
          const timeOffset = props.transcript[index].timeOffset;
          if (isInHighlightedRange(timeOffset)) {
            message.classList.add('highlight');

            if (!scrolled) {
              message.scrollIntoView({ behavior: 'smooth', block: 'center' });
              scrolled = true;
            }
          } else {
            message.classList.remove('highlight');
          }
        });
      }
    };

    watch(() => props.currentVideoSeekTime, () => {
      applyHighlightingBasedOnSeekTime();
    });

    const applyHighlightingBasedOnSeekTime = () => {
      const area = chatArea.value;
      if (area && props.transcript.length > 0 && props.currentVideoSeekTime !== undefined) {
        if (highlightedIndex !== -1) {
          const prevHighlightedMessage = area.querySelector(`.message:nth-child(${highlightedIndex + 1})`);
          if (prevHighlightedMessage) {
            prevHighlightedMessage.classList.remove('highlight-seek-time');
          }
        }

        let closestIndex = -1;

        // Find the index of the transcript closest to or slightly greater than currentVideoSeekTime
        // for (let i = 0; i < props.transcript.length; i++) {
        //   if (props.transcript[i].timeOffset >= props.currentVideoSeekTime) {
        //     closestIndex = i;
        //     break;
        //   }
        // }

        let low = 0;
        let high = props.transcript.length - 1;

        while (low <= high) {
          const mid = Math.floor((low + high) / 2);
          const currentTimeOffset = props.transcript[mid].timeOffset;

          if (currentTimeOffset - props.currentVideoSeekTime <= 0.001) {
            closestIndex = mid;
            low = mid + 1;
          } else {
            high = mid - 1;
          }
        }


        if (closestIndex !== -1) {
          const closestMessage = area.querySelector(`.message:nth-child(${closestIndex+2})`);
          if (closestMessage) {
            closestMessage.classList.add('highlight-seek-time');
            closestMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            highlightedIndex = closestIndex+1;
          }
        }
      }
    };

    const handleTranscriptClick = (message: TranscriptMessage) => {
      // Handle the click event, you can perform actions here
      context.emit('transcript-clicked', message.timeOffset);
    };

    const isTimeInIdentifiedMoment = (timeOffset: number) => {
      if (props.identifiedMoments){
        console.log("masuk", props.identifiedMoments)
        return props.identifiedMoments.some(moment =>
          timeOffset >= moment.timeOffset_start && timeOffset <= moment.timeOffset_end
        );
      }
     
    };
  

    return {
      chatArea,
      messageHighlight,
      handleTranscriptClick,
      isTimeInIdentifiedMoment
    };
  },
});
</script>


<style scoped>
.headline {
  text-align: center;
}

.chat-area {
  border: 1px solid #ccc;
  background: white;
  max-height: 77vh;
  padding: 1em;
  overflow: auto;
  max-width: 40rem;
  margin: 0 auto 2em auto;
  box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1em;
  margin-bottom: 1em;

  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  max-width: 40rem;
  z-index: 2;
  box-sizing: border-box;
  border-radius: 1rem;
}

.message {
  width: 95%;
  border-radius: 10px;
  padding: .5em;
  margin-bottom: .5em;
  margin-top: .5em;
  font-size: .9em;
  text-align: left;
}

.message-in {
  background: #F1F0F0;
  color: black;
}

.highlight {
  background: #ffeca2;
  /* Highlight color */
  /* Add other styles for highlighting */
}

.highlight-seek-time {
  --tw-text-opacity: 1;
  background: rgb(250, 200, 200);
  /* background: var(--tw-bg-opacity, rgba(255, 236, 162, var(--tw-bg-opacity, 1))); Background color from .highlight */
  /* Highlight color */
  /* Add other
   styles for highlighting */
}


.message-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.time {
  text-align: right;
  margin-right: 10px; /* Adjust margin as needed */
}

.content {
  flex-grow: 1;
}

.speaker-1 {
  color: #368a02; /* Text color for Speaker 1 */
}

.speaker-2 {
  color: #0d6efd; /* Text color for Speaker 2 */
}

.highlight-time {
  color: rgb(255, 123, 0); 
}

.margin-right {
  margin-right: 25px; /* Adjust margin as needed */
}

.margin-left {
  margin-left: 25px; /* Adjust margin as needed */
}
</style>