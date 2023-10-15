<template>
  <div v-if="transcript.length != 0" >
    <section ref="chatArea" class="chat-area">
      <h4 class="headline">Transcript</h4>
      <div v-for="(message, index) in transcript" :key="index" class="message message-in" >
        <b>{{ message.timeOffset }}:</b> 
        {{ message.text }} 
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  props: {
    transcript: {
      type: Array as () => Array<{ text: string, timeOffset: number, duration: number }>,
      required: true,
    },
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
  height: 50vh;
  padding: 1em;
  overflow: auto;
  max-width: 400px;
  margin: 0 auto 2em auto;
  box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
}
.message {
  width: 90%;
  border-radius: 10px;
  padding: .5em;
  margin-bottom: .5em;
  font-size: .8em;
}
.message-in {
  background: #F1F0F0;
  color: black;
}

</style>