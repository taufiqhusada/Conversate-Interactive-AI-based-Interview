import axios from 'axios';


export async function postInterviewData(data: {
    sessionID: string;
    username_interviewer: string;
    username_interviewee: string;
    transcript_link: string;
    video_link: string;
  }): Promise<void> {

    let backendURL = import.meta.env.VITE_BACKEND_URL

    const apiUrl = `${backendURL}/interviews`; // Replace with your API URL
  
    try {
      const response = await axios.post(apiUrl, data);
  
      if (response.status === 200) {
        console.log('interveiw data saved successfully:', response.data);
      } else {
        console.error('Failed to send data:', response.status, response.data);
      }
    } catch (error) {
      console.error('Error while sending data:', error);
    }
  }


export async function postInterviewTranscriptData(data: {
    sessionID: string;
    transcript: any;
  }): Promise<void> {

    let backendURL = import.meta.env.VITE_BACKEND_URL

    const apiUrl = `${backendURL}/interviews/transcript`; // Replace with your API URL
  
    try {
      const response = await axios.post(apiUrl, data);
  
      if (response.status === 200) {
        console.log('transcript data saved successfully:', response.data);
      } else {
        console.error('Failed to send data:', response.status, response.data);
      }
    } catch (error) {
      console.error('Error while sending data:', error);
    }
  }