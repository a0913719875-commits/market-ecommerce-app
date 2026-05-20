const express = require('express');
const bodyParser = require('body-parser');
const Ajv = require('ajv');
const events = require('events');
const crypto = require('crypto');

const app = express();
const ajv = new Ajv();
const myEmitter = new events.EventEmitter();

// Schema for payload validation
const payloadSchema = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    event: { type: 'string' },
    data: { type: 'object' }
  },
  required: ['id', 'event', 'data'],
  additionalProperties: false
};

// Simple in-memory storage for recently processed webhook IDs
const processedIds = new Set();

app.use(bodyParser.json());

app.post('/webhook', (req, res) => {
  const payload = req.body;

  // Validate payload schema
  const validate = ajv.compile(payloadSchema);
  if (!validate(payload)) {
    return sendError(res, 'E001', 'Invalid payload schema');
  }

  // Check for duplicate IDs
  const payloadHash = crypto.createHash('sha256').update(payload.id).digest('hex');
  if (processedIds.has(payloadHash)) {
    return sendError(res, 'E002', 'Duplicated webhook event');
  }
  
  // Mark ID as processed
  processedIds.add(payloadHash);
  
  // Set timeout to remove processed event after 10 minutes
  setTimeout(() => processedIds.delete(payloadHash), 600000);
  
  // Simulate processing
  processWebhook(payload)
    .then(() => res.status(200).send('Webhook processed successfully'))
    .catch(err => sendError(res, 'E003', `Error processing webhook: ${err.message}`));
});

// Error handling
function sendError(res, code, message) {
  console.error(`Error code ${code}: ${message}`);
  myEmitter.emit('error', { code, message });
  return res.status(400).json({ error: { code, message } });
}

// Simulate webhook processing logic
function processWebhook(payload) {
  return new Promise((resolve, reject) => {
    // Implement actual processing logic here
    resolve();
  });
}

// Subscribe to error events for notifications
myEmitter.on('error', (err) => {
  console.log('Error Notification:', err);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Webhook handler listening on port ${PORT}`);
});
```

此代碼將會在一個 Express 服務器上運行 webhook 處理程序，使用 JSON Schema 驗證請求內容的正確性，防止重複處理同一請求，並捕獲並通知詳細錯誤碼。