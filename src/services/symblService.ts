// services/symblService.ts
import axios from 'axios';

export default class SymblService {
  async transcribeVideo(videoUrl: string, appId: string, appSecret: string): Promise<Array<{ text: string, timeOffset: number, duration: number }>> {
    try {
        // Authenticate with Symbl.ai
        const authResponse = await axios.post('https://api.symbl.ai/oauth2/token:generate', {
            type: 'application',
            appId,
            appSecret,
        });

        const accessToken = authResponse.data.accessToken;

        console.log(videoUrl);

        // submit video
        const submissionResponse = await axios.post('https://api.symbl.ai/v1/process/video/url', {
            url: videoUrl
        }, {
            headers: {
                accept: 'application/json',
                'content-type': 'application/json',
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        const jobId = submissionResponse.data.jobId;

        // Poll for job completion
        let jobStatus = 'in-progress';

        while (jobStatus !== 'completed') {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for a few seconds before checking again

            const statusResponse = await axios.get(`https://api.symbl.ai/v1/job/${jobId}`, {
                headers: {
                'Authorization': `Bearer ${accessToken}`,
                },
            });

            jobStatus = statusResponse.data.status;
            console.log(jobStatus);
        }

        // Once the job is completed, retrieve the transcript
        const conversationId = submissionResponse.data.conversationId;
        console.log(conversationId)
        const transcriptResponse = await axios.get(`https://api.symbl.ai/v1/conversations/${conversationId}/messages`, {
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
        });
    
        const transcript:never[] = transcriptResponse.data.messages

        const formattedTranscript: Array<{ text: string, timeOffset: number, duration: number }> = transcript.map(item => {
            // You can provide values for the properties as needed
            return {
              text: item["text"],
              timeOffset: item["timeOffset"],
              duration: item["duration"],
            };
          });

        return formattedTranscript;
    } catch (error) {
      console.error('Symbl.ai error:', error);
      throw error;
    }
  }
}