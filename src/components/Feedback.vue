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
            <input v-model="annotation" class="form-control form-control mb-3" type="text" placeholder="Comment">
            <button v-if="!showChatbox" @click="askGPT" class="btn btn-outline-secondary" type="button">Ask
                Feedback</button>
        </form>
        <div v-if="showChatbox" class="chat mt-3">
            <div class="contact">
                <div class="name">Ask For Feedback</div>
            </div>
            <div id="chat-messages" class="messages" ref="messages">
                <div v-for="(message, index) in chatMessages" :key="index">
                    <div :class="message.sender === 'user' ? 'message user' : 'message bot'">
                        <div v-if="message.sender === 'bot' && message.isTyping" class="typing">
                            <div class="dot dot-1"></div>
                            <div class="dot dot-2"></div>
                            <div class="dot dot-3"></div>
                        </div>
                        <div v-else>{{ message.text }}</div>
                    </div>
                </div>
            </div>
            <div class="input">
                <input type="text" v-model="question" placeholder="Type your question here!" @keyup.enter="sendMessage" />
                <i class="fas fa-microphone"></i>
            </div>
        </div>


        <button @click="saveFormData" class="btn btn-primary mt-3 m-1">Save</button>
        <button @click="navigateBack" class="btn btn-secondary mt-3 m-1" :disabled="currentIndex === 0">Back</button>
        <button @click="navigateNext" class="btn btn-secondary mt-3 m-1"
            :disabled="currentIndex === savedData.length">Next</button>
    </div>
</template>
  
  
<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';
import Chatbox from '@/components/chatbox.vue';

type SavedData = {
    secondStart: number;
    secondEnd: number;
    annotation: string;
    question: string;
    feedback: string;
    transcript: string;
    chatMessages: ChatMessage[];
};

interface ChatMessage {
    text: string;
    sender: 'user' | 'bot';
    isTyping: boolean;
}


export default defineComponent({
    components: {
        Chatbox,
    },
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
        }
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
            showChatbox: false,
            chatMessages: [] as ChatMessage[], // Define the type for chatMessages
            backendURL: "http://127.0.0.1:5000",
        };
    },
    methods: {
        async sendMessage() {
            if (this.question.trim() === '') {
                return;
            }

            // Add user message to the chat
            this.chatMessages.push({ text: this.question, sender: 'user', isTyping: false });

            // Simulate a bot response with typing animation
            this.chatMessages.push({ text: 'Bot is typing...', sender: 'bot', isTyping: true });


            this.scrollToBottom();

            const requestBody = {
                comment: this.annotation,
                transcript: this.getTranscript(this.startTime, this.endTime),
                question: this.question,
            };

            this.question = '';

            console.log(requestBody);

            try {

                // Make a POST request to your API
                const response = await axios.post(`${this.backendURL}/feedbacks`, requestBody);

                this.chatMessages.pop();
                if (response.status === 200) {
                    // Update the feedback field with the response from GPT-4
                    this.feedback = response.data.data;
                    this.scrollToBottom();
                    this.chatMessages.push({ text: this.feedback, sender: 'bot', isTyping: false });
                } else {
                    // Handle API response error
                    console.error('Failed to get feedback from GPT-4:', response.status, response.data);
                    this.scrollToBottom();
                    this.chatMessages.push({ text: 'Failed to get feedback from GPT-4', sender: 'bot', isTyping: false });
                }
            } catch (error) {
                // Handle network or other errors
                console.error('Error while requesting feedback from GPT-4:', error);
            }
        },

        async askGPT() {
            this.showChatbox = true;

        },


        getTranscript(startTime: number, endTime: number): string {
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
                chatMessages: this.chatMessages,
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
                    this.chatMessages =  [] as ChatMessage[]

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
                this.chatMessages =  [] as ChatMessage[]

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
            this.chatMessages = savedEntry.chatMessages;
        },

        scrollToBottom() {
            const messagesContainer = this.$refs.messages as HTMLElement;
            if (messagesContainer) {
                this.$nextTick(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                });
            }
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
.contact {
    position: relative;
    /* margin-bottom: 1rem; */
    padding-left: 2rem;
    height: 4.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.name {
    font-weight: 500;
    margin-bottom: 0.125rem;
}

.chat {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 40rem;
    height: 20rem;
    z-index: 2;
    box-sizing: border-box;
    border-radius: 1rem;
    background: white;
    box-shadow:
        0 0 8rem 0 rgba(0, 0, 0, 0.1),
        0rem 2rem 4rem -3rem rgba(0, 0, 0, 0.5);
}

.messages {
    /* padding: 6rem; */
    background: #F7F7F7;
    /* You can update the background color as needed */
    flex-shrink: 2;
    overflow-y: auto;
    box-shadow:
        inset 0 2rem 2rem -2rem rgba(0, 0, 0, 0.05),
        inset 0 -2rem 2rem -2rem rgba(0, 0, 0, 0.05);
}

.message {
    box-sizing: border-box;
    padding: 0.5rem 2rem;
    margin: 1rem;
    background: #FFF;
    border-radius: 1.125rem 1.125rem 1.125rem 0;
    min-height: 2.25rem;
    width: fit-content;
    max-width: 66%;
    box-shadow:
        0 0 2rem rgba(0, 0, 0, 0.075),
        0rem 1rem 1rem -1rem rgba(0, 0, 0, 0.1);
}

.message.user {
    margin: 1rem 1rem 1rem auto;
    border-radius: 1.125rem 1.125rem 0 1.125rem;
    background: #333;
    /* You can update the color as needed */
    color: white;
}

.typing {
    display: flex;
    align-items: center;
}

.dot {
    width: 8px;
    height: 8px;
    background-color: #555;
    border-radius: 50%;
    margin: 0 4px;
    animation: bounce 1s infinite;
}

.dot-1 {
    animation-delay: 0s;
}

.dot-2 {
    animation-delay: 0.2s;
}

.dot-3 {
    animation-delay: 0.4s;
}

@keyframes bounce {

    0%,
    80%,
    100% {
        transform: translateY(0);
    }

    40% {
        transform: translateY(-10px);
    }
}

.input {
    box-sizing: border-box;
    flex-basis: 4rem;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding: 0 0.5rem 0 1.5rem;
}

i {
    font-size: 1.5rem;
    margin-right: 1rem;
    color: #666;
    /* You can update the color as needed */
    cursor: pointer;
    transition: color 200ms;
}

i:hover {
    color: #333;
    /* You can update the color as needed */
}

input {
    border: none;
    background-image: none;
    background-color: white;
    padding: 0.5rem 1rem;
    margin-right: 1rem;
    border-radius: 1.125rem;
    flex-grow: 2;
    box-shadow:
        0 0 1rem rgba(0, 0, 0, 0.1),
        0rem 1rem 1rem -1rem rgba(0, 0, 0, 0.2);
}

input::placeholder {
    color: #999;
    /* You can update the color as needed */
}

.chat {
    opacity: 1;
    transition: opacity 1s;
    /* Adjust the transition duration as needed */
}

.show-chatbox .chat {
    opacity: 0;
}</style>