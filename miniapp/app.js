const state = {
  token: null,
  currentCandidate: null,
  selectedMatchId: null,
  selectedMatchName: "",
};

const statusEl = document.getElementById("status");
const profileSection = document.getElementById("profileSection");
const swipeSection = document.getElementById("swipeSection");
const profileForm = document.getElementById("profileForm");
const candidateCard = document.getElementById("candidateCard");
const matchesList = document.getElementById("matchesList");
const chatSection = document.getElementById("chatSection");
const chatTitle = document.getElementById("chatTitle");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const giftsList = document.getElementById("giftsList");

function setStatus(message) {
  statusEl.textContent = message;
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";

  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "API error");
  return payload;
}

function renderCandidate(candidate) {
  state.currentCandidate = candidate;
  if (!candidate) {
    candidateCard.innerHTML = "No more profiles yet. Try later.";
    return;
  }

  candidateCard.innerHTML = `
    <h3>${candidate.name}, ${candidate.age}</h3>
    <p>📍 ${candidate.city || "Unknown"}</p>
    <p>${candidate.bio || "No bio"}</p>
  `;
}

async function loadCandidate() {
  const data = await api("/api/feed/next");
  renderCandidate(data.candidate);
}

async function doSwipe(action) {
  if (!state.currentCandidate) return;
  const data = await api("/api/swipe", {
    method: "POST",
    body: JSON.stringify({
      to_user_id: state.currentCandidate.user_id,
      action,
    }),
  });

  if (data.match) {
    setStatus("🎉 It's a match!");
  }

  renderCandidate(data.next_candidate);
  await loadMatches();
}

function renderMatches(matches) {
  if (!matches.length) {
    matchesList.innerHTML = "No matches yet.";
    return;
  }

  matchesList.innerHTML = "";
  for (const match of matches) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `💬 ${match.name}, ${match.age}`;
    button.addEventListener("click", () => openChat(match.user_id, match.name));
    matchesList.appendChild(button);
  }
}

async function loadMatches() {
  const data = await api("/api/matches");
  renderMatches(data.matches);
}

async function openChat(otherUserId, name) {
  state.selectedMatchId = otherUserId;
  state.selectedMatchName = name;
  chatSection.classList.remove("hidden");
  chatTitle.textContent = `Chat with ${name}`;

  const data = await api(`/api/chat/${otherUserId}`);
  if (!data.messages.length) {
    chatMessages.innerHTML = "No messages yet.";
    return;
  }

  chatMessages.innerHTML = data.messages
    .map((m) => `<p><strong>${m.from_user_id === otherUserId ? name : "You"}:</strong> ${m.message}</p>`)
    .join("");

  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
  if (!state.selectedMatchId) return;
  const text = chatInput.value.trim();
  if (!text) return;

  await api(`/api/chat/${state.selectedMatchId}`, {
    method: "POST",
    body: JSON.stringify({ message: text }),
  });

  chatInput.value = "";
  await openChat(state.selectedMatchId, state.selectedMatchName);
}

async function sendGift() {
  if (!state.selectedMatchId) return;
  const giftCode = document.getElementById("giftSelect").value;
  await api("/api/gifts/send", {
    method: "POST",
    body: JSON.stringify({ to_user_id: state.selectedMatchId, gift_code: giftCode, gift_message: "" }),
  });
  setStatus("Gift sent");
  await loadReceivedGifts();
}

async function loadReceivedGifts() {
  const data = await api("/api/gifts/received");
  if (!data.gifts.length) {
    giftsList.innerHTML = "No gifts yet.";
    return;
  }

  giftsList.innerHTML = data.gifts
    .map((g) => `<div>🎁 ${g.gift_name} from ${g.from_name}</div>`)
    .join("");
}

async function submitProfile(event) {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());
  payload.age = Number(payload.age);

  await api("/api/profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  profileSection.classList.add("hidden");
  swipeSection.classList.remove("hidden");
  await loadCandidate();
  await loadMatches();
}

async function shareBot() {
  const data = await api("/api/share-link");
  if (window.Telegram?.WebApp?.openTelegramLink) {
    window.Telegram.WebApp.openTelegramLink(data.share_url);
  } else {
    window.open(data.share_url, "_blank");
  }
}

async function init() {
  try {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setStatus("Open this page inside Telegram Mini App");
      return;
    }

    tg.ready();
    tg.expand();

    setStatus("Authorizing with Telegram...");
    const auth = await api("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ initData: tg.initData }),
    });

    state.token = auth.token;
    const me = await api("/api/me");

    if (!me.profile_complete) {
      setStatus("Complete your profile to start swiping");
      profileSection.classList.remove("hidden");
      swipeSection.classList.add("hidden");
    } else {
      setStatus("Ready");
      profileSection.classList.add("hidden");
      swipeSection.classList.remove("hidden");
      await loadCandidate();
    }

    await loadMatches();
    await loadReceivedGifts();
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

document.getElementById("likeBtn").addEventListener("click", () => doSwipe("like"));
document.getElementById("dislikeBtn").addEventListener("click", () => doSwipe("dislike"));
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("giftBtn").addEventListener("click", sendGift);
document.getElementById("refreshBtn").addEventListener("click", init);
document.getElementById("shareBtn").addEventListener("click", shareBot);
profileForm.addEventListener("submit", submitProfile);

init();
