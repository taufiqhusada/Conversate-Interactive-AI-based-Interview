
import type TheFooterVue from './components/TheFooter.vue';
<template>
  <TheHeader></TheHeader>
  <div class="container">
    <br>
    <h1>Mock Interview Annotation Tool</h1>
    <div class="row">
        <div class="col-sm-6">
            <VideoUploader @transcript-updated="updateTranscript"  />
            <AnnotationTextboxes :showAnnotationTextboxes="showAnnotationTextboxes" :transcript="transcript" :sessionID="sessionID"/> 
        </div>
        <div class="col-sm-6">
          <TranscriptDisplay :transcript="transcript"/>
          <Feedback :initial-settings="{ updateSettings }"/>
        </div>
    </div>
  </div>
  <TheFooter></TheFooter>
</template>

<script lang="ts">
import { ref } from 'vue';
import VideoUploader from '@/components/VideoUploader.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import AnnotationTextboxes from '@/components/AnnotationTextboxes.vue';
import TheHeader from './components/TheHeader.vue';
import TheFooter from './components/TheFooter.vue';
import Feedback from '@/components/Feedback.vue';

export default {
  components: {
    VideoUploader,
    TranscriptDisplay,
    AnnotationTextboxes,
    TheHeader,
    TheFooter,
    Feedback,
},
  setup() {
    const transcript = ref([]);
    const showAnnotationTextboxes = ref(false)
    const sessionID = ref("")
    // Method to update the transcript when it is obtained
    const updateTranscript = (newTranscript: never[], passedSessionID:string) => {
      console.log("called in");
      console.log(newTranscript);
      transcript.value = newTranscript;

      showAnnotationTextboxes.value = true;
      sessionID.value = passedSessionID
    };
    
    return {
      transcript,
      updateTranscript,
      showAnnotationTextboxes,
      sessionID,
    };
  },
};
</script>

<style scoped>
.row {
  display: inline-block;
  width: 50%;
  height: auto;
  overflow-y: auto;
}

.column {
  display: inline-block;
  width: 50%;
  height: auto;
  overflow-y: auto;
}


</style>