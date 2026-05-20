const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // in milliseconds

let webhookFailures = 0;

function sendWebhook(data, retries = 0) {
    axios.post('https://webhook.url/endpoint', data)
        .then(response => {
            console.log('Webhook sent successfully:', response.status);
        })
        .catch(error => {
            console.error('Webhook failed:', error.message);
            webhookFailures++;
            if (retries < MAX_RETRIES) {
                setTimeout(() => sendWebhook(data, retries + 1), RETRY_DELAY);
            }
        });
}

app.post('/trigger-webhook', (req, res) => {
    const data = req.body;
    sendWebhook(data);
    res.send('Webhook process started');
});

app.get('/webhook-stats', (req, res) => {
    res.json({ webhookFailures });
});

// CTO AI Daily Inspection API Integration
app.get('/cto-daily-report', (req, res) => {
    const report = generateDailyReport();
    res.json(report);
});

function generateDailyReport() {
    return {
        status: 'OK',
        webhookFailures,
        timestamp: new Date().toISOString()
    };
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});