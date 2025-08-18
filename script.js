const API_BASE = "https://leadhunterai-backend-3.onrender.com";
let searchResults = [];
let prospects = JSON.parse(localStorage.getItem('prospects') || '[]');

// DOM
const $ = id => document.getElementById(id);
const keywordInput = $('keyword-input');
const resultsSection = $('results-section');
const resultsList = $('results-list');
const contextInput = $('context-input');
const serviceInput = $('service-input');
const locationInput = $('location-input');
const messageOutput = $('message-output');
const messageText = $('message-text');
const searchSpinner = $('search-spinner');
const generateSpinner = $('generate-spinner');
const notification = $('notification');
const saveProspectBtn = $('save-prospect');

// === Search ===
async function search() {
  const keyword = keywordInput.value.trim();
  const platforms = Array.from($('platform-select').selectedOptions).map(o => o.value).join(',');
  
  if (!keyword) return showNotification("Enter a keyword", true);

  searchSpinner.classList.remove('hidden');
  resultsSection.classList.add('hidden');

  try {
    const res = await fetch(`${API_BASE}/search?keyword=${encodeURIComponent(keyword)}&platforms=${platforms}`);
    const data = await res.json();
    
    if (data.results?.length) {
      searchResults = data.results;
      displayResults();
      resultsSection.classList.remove('hidden');
    } else {
      resultsList.innerHTML = '<p class="text-gray-600">No leads found. Try a different keyword.</p>';
      resultsSection.classList.remove('hidden');
    }
  } catch (err) {
    console.error(err);
    showNotification("Failed to fetch leads", true);
  } finally {
    searchSpinner.classList.add('hidden');
  }
}

function displayResults() {
  resultsList.innerHTML = searchResults.map(r => `
    <div class="border rounded-lg p-4 hover:shadow-sm">
      <div class="flex justify-between">
        <span class="text-xs font-semibold px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded">${r.platform}</span>
        <span class="text-xs px-2 py-1 rounded ${
          r.lead_score.includes("Hot") ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200" : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
        }">${r.lead_score}</span>
      </div>
      <h3 class="font-medium mt-1">
        <a href="${r.url}" target="_blank" class="hover:underline text-primary">${r.title}</a>
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">${r.snippet}</p>
      <button onclick="useAsContext(${searchResults.indexOf(r)})"
              class="mt-2 text-xs bg-primary text-white px-3 py-1 rounded hover:bg-indigo-700 transition">
        Use as Context
      </button>
    </div>
  `).join('');
}

function useAsContext(index) {
  const r = searchResults[index];
  contextInput.value = r.snippet;
  if (r.detected_service) serviceInput.value = r.detected_service;
  if (r.detected_location) locationInput.value = r.detected_location;
  messageOutput.classList.add('hidden');
  saveProspectBtn.classList.remove('hidden');
  showNotification("Context set!");
}

// === Generate ===
async function generate() {
  const service = serviceInput.value.trim();
  const tone = $('tone-input').value.trim();
  const location = locationInput.value.trim();
  const context = contextInput.value.trim();

  if (!service || !context) {
    showNotification("Service and context required", true);
    return;
  }

  generateSpinner.classList.remove('hidden');
  try {
    const res = await fetch(`${API_BASE}/generate_message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ service, tone, location, context })
    });
    const data = await res.json();
    if (data.message) {
      messageText.value = data.message;
      messageOutput.classList.remove('hidden');
    } else {
      throw new Error(data.error);
    }
  } catch (err) {
    showNotification("AI failed: " + err.message, true);
  } finally {
    generateSpinner.classList.add('hidden');
  }
}

// === Copy ===
function copyMessage() {
  navigator.clipboard.writeText(messageText.value).then(() => {
    showNotification("Copied!");
  });
}

// === Prospects ===
function updateProspects() {
  const list = $('prospects-list');
  list.innerHTML = prospects.map(p => `
    <div class="border-b pb-2">
      <div><strong>${p.service}</strong> in ${p.location}</div>
      <div class="text-gray-600 text-xs">${p.platform}: <a href="${p.url}" target="_blank" class="underline">Go</a></div>
    </div>
  `).join('');
}

saveProspectBtn.addEventListener('click', () => {
  const context = contextInput.value.substring(0, 100) + "...";
  const prospect = {
    service: serviceInput.value,
    location: locationInput.value,
    platform: "Custom",
    url: "#manual",
    timestamp: new Date().toISOString()
  };
  prospects.unshift(prospect);
  localStorage.setItem('prospects', JSON.stringify(prospects));
  updateProspects();
  saveProspectBtn.classList.add('hidden');
  showNotification("Lead saved!");
});

// === Notifications ===
function showNotification(msg, isError = false) {
  notification.textContent = msg;
  notification.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg transition-opacity duration-300 ${isError ? 'bg-red-600' : 'bg-green-600'} text-white`;
  notification.classList.remove('hidden');
  setTimeout(() => notification.classList.add('opacity-0'), 3000);
  setTimeout(() => notification.classList.add('hidden'), 3500);
}

// Init
updateProspects();