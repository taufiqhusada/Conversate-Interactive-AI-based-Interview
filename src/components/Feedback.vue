<template>
    <div v-if="showAnnotationTextboxes" class="mt-3">
        <h4>Annotation</h4>
        <form>
            <div class="form-group row mb-3">
                <div class="col">
                    <div class="input-group">
                        <span class="input-group-btn">
                            <button class="btn btn-default pin-button" type="button" @click="getTime('start')">
                                <img src="/images/pin.png" alt="Pin" class="pin-icon">
                            </button>
                        </span>
                        <input type="text" class="form-control time-input" v-model="startTimeHHMMSS" placeholder="Start Time (hh:mm:ss)">
                    </div>
                </div>
                <div class="col">
                    <div class="input-group">
                        <span class="input-group-btn">
                            <button class="btn btn-default pin-button" type="button" @click="getTime('end')">
                                <img src="/images/pin.png" alt="Pin" class="pin-icon">
                            </button>
                        </span>
                        <input type="text" class="form-control time-input" v-model="endTimeHHMMSS" placeholder="End Time (hh:mm:ss)">
                    </div>
                </div>
            </div>
            <input v-model="annotation" class="form-control form-control mb-3" type="text" placeholder="Self Assesment / Comment" list="commentOptions">
            <datalist id="commentOptions">
                <option value="I am not giving enough example"></option>
                <option value="I am good at answering the interview question"></option>
                <option value="I am bad at answering the interview question"></option>
                <option value="There is some good and bad part when I answer this interview question"></option>
                <option value="I am not sure about my performance in this part"></option>
            </datalist>
            <button v-if="!showChatbox" @click="askGPT" class="btn btn-outline-secondary" type="button">Open Feedback Chat Window</button>
        </form>
        <div v-if="showChatbox" class="chat mt-3">
            <div class="contact">
                <div class="name">Ask Feedback</div>
            </div>
            <div id="chat-messages" class="messages" ref="messages">
                <div v-for="(message, index) in chatMessages" :key="index">
                    <div :class="message.role === 'user' ? 'message user' : 'message bot'">
                        <div v-if="message.role === 'assistant' && message.isTyping" class="typing">
                            <div class="dot dot-1"></div>
                            <div class="dot dot-2"></div>
                            <div class="dot dot-3"></div>
                        </div>
                        <div v-else v-html="message.content"></div>

                        <div v-if="message.dropdownItems">
                            <div class="dropdown m-2" @click="toggleDropdown">
                                <button class="btn btn-outline-dark">Select Question</button>
                                <div class="dropdown-menu" v-show="isDropdownOpen">
                                    <a v-for="(item, index) in message.dropdownItems" :key="index" class="dropdown-item" @click="selectDropdownItem(item)">{{ item }}</a>
                                </div>
                            </div>
                            <br>
                            <p>Or you can type in your question</p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="input">
                <input type="text" v-model="question" placeholder="Type your question here!" @keyup.enter="sendMessage"  ref="questionInputRef"/>
                <i class="fas fa-microphone" @click="toggleRecording" :class="{ 'recording': isRecording }">&#xf130;</i>
            </div>
        </div>


        <button @click="saveFormData" class="btn btn-primary mt-3 m-1">Save</button>
        <button @click="navigateBack" class="btn btn-secondary mt-3 m-1" :disabled="currentIndex === -1">Back</button>
        <button @click="navigateNext" class="btn btn-secondary mt-3 m-1"
            :disabled="savedData.length === 0 || currentIndex === savedData.length">Next</button>
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
    chatMessages: ChatMessage[];
    id: string;
};

interface ChatMessage {
    content: string;
    role: 'user' | 'assistant';
    isTyping?: boolean;
    dropdownItems?: string[];
}

interface ChatMessageBackend {
    content: string;
    role: 'user' | 'assistant';
}


export default defineComponent({
    props: {
        showAnnotationTextboxes: {
            type: Boolean,
            required: true,
        },
        transcript: {
            type: Array as () => Array<{ text: string, timeOffset: number, duration: number, speaker: string }>,
            required: true,
        },
        sessionID: {
            type: String,
            required: true,
        },
        currentVideoSeekTime: {
            type: Number,
        }
    },
    data() {
        return {
            startTimeHHMMSS: '',
            endTimeHHMMSS: '',
            annotation: '',
            question: ref<string>(''),
            feedback: '',
            concatenatedFilteredTranscript: '',
            savedData: [] as SavedData[], // Array to store saved data
            currentIndex: -1,
            showChatbox: ref(false),
            chatMessages: [] as ChatMessage[], // Define the type for chatMessages
            backendURL: '/api',
            isRecording: ref<boolean>(false),
            recognition: null as SpeechRecognition | null,
            isDropdownOpen: ref(false),
        };
    },
    methods: {
        // Function to convert HH:MM:SS format to seconds
        convertHHMMSSToSeconds(timeString: string): number {
            const [hours, minutes, seconds] = timeString.split(':').map(Number);
            return hours * 3600 + minutes * 60 + seconds;
        },
        // Function to convert seconds to HH:MM:SS format
        convertSecondsToHHMMSS(seconds: number): string {
            const date = new Date(seconds * 1000);
            return date.toISOString().substring(11, 19);
        },

        async sendMessage() {
            if (this.question.trim() === '') {
                return;
            }

            // Add user message to the chat
            this.chatMessages.push({ content: this.question, role: 'user', isTyping: false });

            // Simulate a bot response with typing animation
            this.chatMessages.push({ content: 'Bot is typing...', role: 'assistant', isTyping: true });


            this.scrollToBottom();


            const requestBody = {
                comment: this.annotation,
                transcript: this.getTranscript(this.convertHHMMSSToSeconds(this.startTimeHHMMSS), this.convertHHMMSSToSeconds(this.endTimeHHMMSS)),
                messages: this.mapChatMessagesToBackendFormat(this.chatMessages.slice(0, -1))
            };

            this.question = '';


            try {
                // Make a POST request to your API
                const response = await axios.post(`${this.backendURL}/feedbacks/conversation`, requestBody);
                this.chatMessages.pop();
                if (response.status === 200) {
                    // Update the feedback field with the response from GPT-4
                    this.scrollToBottom();
                    const repliedMessage = response.data.data;
                    this.chatMessages.push({ content: repliedMessage, role: 'assistant', isTyping: false});
                    if (this.chatMessages.length == 4) {
                        this.chatMessages.push({ content: "Do you want to try saying this part again in a better way? I can give you feedback again based on that", role: 'assistant', isTyping: false });
                    }
                } else {
                    // Handle API response error
                    console.error('Failed to get chat from GPT-4:', response.status, response.data);
                    this.scrollToBottom();
                }
            } catch (error) {
                // Handle network or other errors
                console.error('Error while chatting with GPT-4:', error);
            }


        },

        mapChatMessagesToBackendFormat(chatMessages: ChatMessage[]) {
            const chatMessagesWithoutTyping = chatMessages.map(({ isTyping,  dropdownItems, ...rest }) => rest);
            return chatMessagesWithoutTyping;
        },

        
        async askGPT() {
            this.showChatbox = true;

            // Send initial message with a dropdown when chatbox is shown
            this.chatMessages.push({
                content: "Hi, what can I help you with?",
                role: 'assistant',
                isTyping: false,
            });
            this.chatMessages.push({
                content: `Try asking these questions`,
                role: 'assistant',
                isTyping: false,
                dropdownItems: [
                    'How to improve this part?',
                    'Could you give me example how to answer this using STAR method?',
                    'How is my performance on this part?',
                    'Could you give me example how to answer this better?',
                    'What is good about this part?',
                ] as string[]
            });
        },

        toggleDropdown() {
            this.isDropdownOpen = !this.isDropdownOpen;
        },

        selectDropdownItem(selectedValue: string) {
            this.question = selectedValue;

            this.sendMessage();
        },

        getTranscript(startTime: number, endTime: number): string {
            const filteredTranscript = this.transcript.filter(entry => {
                return entry.timeOffset >= startTime && entry.timeOffset <= endTime;
            });

            this.concatenatedFilteredTranscript = filteredTranscript.map(entry => entry.speaker + ":" + entry.text).join('\n')

            return this.concatenatedFilteredTranscript
        },

        async saveFormData() {
            try {
                const dataToSave = {
                    secondStart: this.convertHHMMSSToSeconds(this.startTimeHHMMSS),
                    secondEnd: this.convertHHMMSSToSeconds(this.endTimeHHMMSS),
                    annotation: this.annotation,
                    feedback: this.feedback,
                    transcript: this.concatenatedFilteredTranscript,
                    question: this.question,
                    chatMessages: this.chatMessages,
                } as SavedData;

                if (this.currentIndex >= 0 && this.currentIndex < this.savedData.length) { // update data
                    // Make a PUT request to your update API

                    const currentId = this.savedData[this.currentIndex].id
                    dataToSave.id = currentId;

                    this.savedData[this.currentIndex] = dataToSave;
                    const response = await axios.put(`${this.backendURL}/interviews/${this.sessionID}/annotations/${currentId}`, dataToSave);

                    if (response.status === 200) {
                        console.log('annotation updated successfully:');

                        this.startTimeHHMMSS = "";
                        this.endTimeHHMMSS = "";
                        this.annotation = '';
                        this.question = '';
                        this.feedback = '';
                        this.chatMessages = [] as ChatMessage[]

                        // Update the currentIndex to the last saved entry
                        this.currentIndex = this.savedData.length;
                        this.showChatbox = false;

                        this.$emit('save-data', this.currentIndex)
                    } else {
                        console.error('Failed to save data:', response.status, response.data);
                    }
                } else {
                    // Make a POST request to your save API
                    const response = await axios.post(`${this.backendURL}/interviews/${this.sessionID}/annotations`, dataToSave);

                    if (response.status === 200) {
                        console.log('annotation saved successfully:');

                        this.startTimeHHMMSS = "";
                        this.endTimeHHMMSS = "";
                        this.annotation = '';
                        this.question = '';
                        this.feedback = '';
                        this.chatMessages = [] as ChatMessage[]

                        // Push the saved data to the savedData array
                        dataToSave.id = response.data['data']['id']
                        this.savedData.push(dataToSave);

                        // Update the currentIndex to the last saved entry
                        this.currentIndex = this.savedData.length;
                        this.showChatbox = false;

                        this.$emit('save-data', this.currentIndex)
                    } else {
                        console.error('Failed to save data:', response.status, response.data);
                    }
                }
            } catch (error) {
                console.error('Error while saving data:', error);
            }
        },

        navigateBack() {
            if (this.currentIndex > -1) {
                // Decrement the currentIndex to go back to the previous entry
                this.currentIndex--;
                // Update the form fields with the selected saved data
                this.loadSavedData();
                this.showChatbox = true;
            }
        },
        navigateNext() {
            if (this.currentIndex < this.savedData.length - 1) {
                // Increment the currentIndex to go to the next entry
                this.currentIndex++;
                // Update the form fields with the selected saved data
                this.loadSavedData();
            } else {
                this.showChatbox = false;

                this.startTimeHHMMSS = "";
                this.endTimeHHMMSS = "";
                this.annotation = '';
                this.question = '';
                this.feedback = '';
                this.chatMessages = [] as ChatMessage[]

                this.currentIndex++;
            }
        },
        loadSavedData() {
            // Load the form fields with the data from the savedData array at the currentIndex
            const savedEntry = this.savedData[this.currentIndex];
            this.startTimeHHMMSS = this.convertSecondsToHHMMSS(savedEntry.secondStart);
            this.endTimeHHMMSS = this.convertSecondsToHHMMSS(savedEntry.secondEnd);
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

        isValidTimeFormat(time: string): boolean {
            const timeRegex = /^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$/;
            return timeRegex.test(time);
        },

        async highlightTranscript() {
            if (this.isValidTimeFormat(this.startTimeHHMMSS) && this.isValidTimeFormat(this.endTimeHHMMSS)) {
                // Emit the updated startTime and endTime to the parent component
                this.$emit('highlight-transcript', [this.convertHHMMSSToSeconds(this.startTimeHHMMSS), this.convertHHMMSSToSeconds(this.endTimeHHMMSS)]);
            }
        },

        toggleRecording() {
            if (this.isRecording) {
                // Stop recording
                if (this.recognition) {
                    this.recognition.stop();
                    this.recognition.onresult = null; // Remove the onresult event handler
                    this.isRecording = false;
                }
            } else {
                // Start recording
                this.recognition = new webkitSpeechRecognition;
                this.recognition.lang = 'en-US';

                this.recognition.continuous = true
                this.recognition.interimResults = true

                // Event handler when speech is recognized
                this.recognition.onresult = (evt: SpeechRecognitionEvent) => {
                    const t = Array.from(evt.results)
                        .map(result => result[0])
                        .map(result => result.transcript)
                        .join('')

                    this.question = t;

                    const textInput = this.$refs.questionInputRef  as HTMLInputElement;
                        if (textInput) {
                            textInput.scrollLeft = textInput.scrollWidth;
                        }
                };

                // // Event handler when speech recognition is stopped
                // this.recognition.onend = () => {
                //     this.isRecording = false;
                // };

                // Start recognition
                this.recognition.start();
                this.isRecording = true;

                const textInput = this.$refs.questionInputRef  as HTMLInputElement;
                if (textInput) {
                    console.log("focus")
                    textInput.focus();
                }
            }
        },


        getTime(id: string){
            if (this.currentVideoSeekTime) {
                if (id=='start'){
                    this.startTimeHHMMSS = this.convertSecondsToHHMMSS(this.currentVideoSeekTime)
                    this.$emit('pin-moment', true, this.currentVideoSeekTime)
                } else {
                    this.endTimeHHMMSS = this.convertSecondsToHHMMSS(this.currentVideoSeekTime + 1)
                    this.$emit('pin-moment', false, this.currentVideoSeekTime)
                }
            }
        }
    },

    watch: {
        startTimeHHMMSS(newValue) {
            // When startTime changes, emit the changes to the parent component
            this.highlightTranscript();
        },
        endTimeHHMMSS(newValue) {
            // When endTime changes, emit the changes to the parent component
            this.highlightTranscript();
        },
    },
});
</script>
  
<style scoped>
.contact {
    position: relative;
    padding-left: 2rem;
    height: 3rem;
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
    max-width: 100%;
    height: 54vh;
    z-index: 2;
    box-sizing: border-box;
    border-radius: 1rem;
    background: white;
    box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
}

.messages {
    /* padding: 6rem; */
    background: #F7F7F7;
    /* You can update the background color as needed */
    flex-shrink: 10;  
    overflow-y: auto;
    height: 30rem;
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
    box-shadow: 2px 2px 5px 2px rgba(0, 0, 0, 0.3);
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
}

.recording {
    color: red;
    /* Change the color to red when recording */
    animation: pulse 1s infinite;
    /* Add a pulsating animation */
}

@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }

    100% {
        transform: scale(1);
    }
}

/* Custom styles for the dropdown */
.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-button {
    background-color: #6c757d;
    color: #fff;
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.dropdown-menu {
    display: none;
    position: absolute;
    background-color: #fff;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    z-index: 1;
    min-width: 160px;
}

.dropdown-item {
    padding: 8px 12px;
    text-decoration: none;
    display: block;
    color: #333;
}

.dropdown-item:hover {
    background-color: #f8f9fa;
}

.dropdown:hover .dropdown-menu {
    display: block;
}

@keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

/* Apply the animation to the chatbox */
.message {
    animation: fadeIn 0.5s ease-in-out;
}
.input-group {
  display: flex;
  align-items: center;
}

.time-input {
  flex-grow: 1;
  border: none; /* Remove input border */
}

.input-group-btn {
  padding: 0; /* Remove padding */
  
  border: none;
    background-image: none;
    padding: 0.1rem;
    border-radius: 1.125rem;
    box-shadow: 1px 2px 5px 1px rgba(0, 0, 0, 0.3);
}

.pin-button {
  padding: 0.375rem 0.75rem;
  margin-right: -1px;
  border-top-left-radius: 1.125rem;
  border-bottom-left-radius: 1.125rem;
}

.pin-button:hover {
  background-color: #e2e6ea; /* Slightly different background on hover/focus for feedback */
}

.pin-icon {
  width: 16px; /* Or any other size */
  height: auto;
}
</style>