<template>
  <div v-if="transcript.length !== 0">
    <section ref="chatArea" class="chat-area">
      <h4 class="headline">Transcript</h4>
      <div v-for="(message, index) in transcript" :key="index" :class="messageHighlight(message)">
        <b>{{ message.timeOffset }}:</b> 
        {{ message.text }} 
      </div>
    </section>
  </div>
</template>


<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

interface TranscriptMessage {
  text: string;
  timeOffset: number;
  duration: number;
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
  },
  setup(props) {
    const chatArea = ref<HTMLElement | null>(null);

    const messageHighlight = (message: TranscriptMessage) => {
      return isInHighlightedRange(message.timeOffset) ? 'message message-in highlight' : 'message message-in';
    };

    const isInHighlightedRange = (timeOffset: number) => {
      return props.timestampHighlights.some(([start, end]) => timeOffset >= start && timeOffset <= end);
    };

    watch(() => props.timestampHighlights, () => {
      applyHighlighting();
    });

    const applyHighlighting = () => {
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

    return {
      chatArea,
      messageHighlight,
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
  height: 33vh;
  padding: 1em;
  overflow: auto;
  width: 40rem;
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
  width: 40rem;
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
  font-size: .8em;
}
.message-in {
  background: #F1F0F0;
  color: black;
}

.highlight {
  background: #ffd427; /* Highlight color */
  /* Add other styles for highlighting */
}

</style>