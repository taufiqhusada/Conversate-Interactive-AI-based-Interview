<template>
  <div class="container">
    <br>
    <h1>Mock Interview Annotation Tool</h1>
    <div class="row">
        <div class="col-sm-6">
            <VideoUploader @transcript-updated="updateTranscript"  />
            <AnnotationTextboxes :showAnnotationTextboxes="showAnnotationTextboxes" :transcript="transcript" :sessionID="sessionID"/> 
        </div>
        <TranscriptDisplay :transcript="transcript" class="col-sm-6"/>
    </div>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import VideoUploader from '@/components/VideoUploader.vue';
import TranscriptDisplay from '@/components/TranscriptDisplay.vue';
import AnnotationTextboxes from '@/components/AnnotationTextboxes.vue';

export default {
  components: {
    VideoUploader,
    TranscriptDisplay,
    AnnotationTextboxes
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

</style>