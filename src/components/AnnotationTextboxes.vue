<template>
    <div v-if="showAnnotationTextboxes" class="mt-3">
      <h4>Annotation</h4>
      <form>
        <div class="form-group row mb-3">
          <div class="col">
            <input v-model="startTime" class="form-control" type="number" placeholder="Start Time">
          </div>
          <div class="col">
            <input v-model="endTime" class="form-control" type="number" placeholder="End Time">
          </div>
        </div>
        <input v-model="annotation" class="form-control form-control mb-3" type="text" placeholder="Annotation">
        <div class="input-group mb-3">
          <input v-model="question" type="text" class="form-control" placeholder="Question to ask GPT-4">
          <div class="input-group-append">
            <button @click="askGPT" class="btn btn-outline-secondary" type="button">Ask</button>
          </div>
        </div>
        <textarea v-model="feedback" class="form-control" type="text" placeholder="Feedback from GPT-4" readonly rows="3"></textarea>
      </form>

    <button @click="saveFormData" class="btn btn-primary mt-3 mr-5">Save</button>
    <button @click="navigateBack" class="btn btn-secondary mt-3 mr-5" :disabled="currentIndex === 0">Back</button>
    <button @click="navigateNext" class="btn btn-secondary mt-3 mr-5" :disabled="currentIndex === savedData.length">Next</button>
    </div>
</template>
  
  
<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';

type SavedData = {
  secondStart: number;
  secondEnd: number;
  annotation: string;
  question: string;
  feedback: string;
  transcript: string;
};

  
  export default defineComponent({
    props: {
        showAnnotationTextboxes: {
            type: Boolean,
            required: true,
        },
        transcript: {
            type: Array as () => Array<{ text: string, timeOffset: number, duration: number }>,
            required: true,
        },
        sessionID: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            startTime: 0.0,
            endTime: 0.0,
            annotation: '',
            question: '',
            feedback: '',
            concatenatedFilteredTranscript: '',
            savedData: [] as SavedData[], // Array to store saved data
            currentIndex: -1,
            backendURL: "http://127.0.0.1:5000",
        };
    },
    methods: {
        async askGPT() {
        // Construct the request body based on the form inputs
            const requestBody = {
                comment: this.annotation,
                transcript: this.getTranscript(this.startTime, this.endTime),
                question: this.question,
            };

            try {
            
                // Make a POST request to your API
                const response = await axios.post(`${this.backendURL}/feedbacks`, requestBody);

                if (response.status === 200) {
                    // Update the feedback field with the response from GPT-4
                    this.feedback = response.data.data;
                } else {
                    // Handle API response error
                    console.error('Failed to get feedback from GPT-4:', response.status, response.data);
                }
            } catch (error) {
                // Handle network or other errors
                console.error('Error while requesting feedback from GPT-4:', error);
            }
        },
        
       
        getTranscript(startTime: number, endTime: number): string{
            const filteredTranscript = this.transcript.filter(entry => {
                return entry.timeOffset >= startTime && entry.timeOffset <= endTime;
            });

            this.concatenatedFilteredTranscript = filteredTranscript.map(entry => entry.text).join('\n')
    
            return this.concatenatedFilteredTranscript
        },

        async saveFormData() {
        // Construct the data to save to your API
            const dataToSave = {
                secondStart: this.startTime,
                secondEnd: this.endTime,
                annotation: this.annotation,
                feedback: this.feedback,
                transcript: this.concatenatedFilteredTranscript,
                question: this.question,
            } as SavedData;

            try {
                // Make a POST request to your save API
                const response = await axios.post(`${this.backendURL}/interviews/${this.sessionID}/annotations`, dataToSave);

                if (response.status === 200) {
                    console.log('annotation saved successfully:', response.data);
                    this.startTime = 0.0;
                    this.endTime = 0.0;
                    this.annotation = '';
                    this.question = '';
                    this.feedback = '';

                    // Push the saved data to the savedData array
                    this.savedData.push(dataToSave);

                    // Update the currentIndex to the last saved entry
                    this.currentIndex = this.savedData.length;
                } else {
                    console.error('Failed to save data:', response.status, response.data);
                }
            } catch (error) {
                console.error('Error while saving data:', error);
            }
        },

        navigateBack() {
            if (this.currentIndex > 0) {
                // Decrement the currentIndex to go back to the previous entry
                this.currentIndex--;
                // Update the form fields with the selected saved data
                this.loadSavedData();
            }
        },
        navigateNext() {
            if (this.currentIndex < this.savedData.length - 1) {
                // Increment the currentIndex to go to the next entry
                this.currentIndex++;
                // Update the form fields with the selected saved data
                this.loadSavedData();
            } else {
                this.startTime = 0.0;
                this.endTime = 0.0;
                this.annotation = '';
                this.question = '';
                this.feedback = '';

                this.currentIndex++;
            }
        },
        loadSavedData() {
            // Load the form fields with the data from the savedData array at the currentIndex
            const savedEntry = this.savedData[this.currentIndex];
            this.startTime = savedEntry.secondStart;
            this.endTime = savedEntry.secondEnd;
            this.annotation = savedEntry.annotation;
            this.feedback = savedEntry.feedback;
            this.question = savedEntry.question;
        },
    },

    watch: {
        async showAnnotationTextboxes(newValue) {
            if (newValue === true) {
                try {
                const response = await axios.get(`${this.backendURL}/interviews/${this.sessionID}/annotations`);

                if (response.status === 200) {
                    this.savedData = response.data.data.annotations; // Assuming the API returns an array of saved data
                    this.currentIndex = this.savedData.length - 1;
                } else {
                    console.error('Failed to fetch saved data:', response.status, response.data);
                }
                } catch (error) {
                    console.error('Error while fetching saved data:', error);
                }
            }
        },
    },
});
</script>
  
<style scoped>


</style>