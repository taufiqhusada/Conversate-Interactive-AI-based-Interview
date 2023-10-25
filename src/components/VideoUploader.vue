<template>
  <div>
    <div class="form-group">
      <input type="file" @change="uploadVideo" accept="video/*" />
    </div>
    <video v-if="videoUrl" controls width="480" height="270">
      <source :src="videoUrl" type="video/mp4" />
    </video>
  </div>
</template>

<script lang="ts">
import { ref,defineComponent } from 'vue';
import firebase from 'firebase/app';
import 'firebase/storage';
import SymblService from '@/services/symblService';
import process from 'process';

export default defineComponent({
  setup(props, context) {
    const videoUrl = ref<string | null>(null);    

    const uploadVideo = async (event: Event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        const storageRef = firebase.storage().ref(`videos/${file.name}`);

        try {
          await storageRef.put(file);
          const downloadURL = await storageRef.getDownloadURL();
          videoUrl.value = downloadURL;

          // Call Symbl.ai to transcribe the video here
          const appId = import.meta.env.VITE_SYMBL_APP_ID; // Replace with your Symbl.ai App ID
          const appSecret = import.meta.env.VITE_SYMBL_APP_SECRET; // Replace with your Symbl.ai App Secret
          const symblService = new SymblService();

          try {
            const transcript = await symblService.transcribeVideo(videoUrl.value || '', appId, appSecret);
            console.log('Transcript:', transcript);

            context.emit('transcript-updated', transcript)
          } catch (error) {
            console.error('Error transcribing video:', error);
          }
         
        } catch (error) {
          console.error('Error uploading video:', error);
        }
      }
    };

    return {
      videoUrl,
      uploadVideo,
    };
  },
});
</script>

