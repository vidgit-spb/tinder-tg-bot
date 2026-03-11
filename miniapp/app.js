const state = {
  token: null,
  me: null,
  currentCandidate: null,
  selectedMatchId: null,
  selectedMatchName: "",
  language: localStorage.getItem("miniapp_lang") || "en",
};

const i18n = {
  en: { title: "💕 Dating MVP", share: "Share", profile: "Complete profile", swipe: "Swipe", matches: "Matches", settings: "Settings", receivedGifts: "Received gifts", myProfile: "My profile", pass: "⬅️ Pass", like: "❤️ Like", send: "Send", statusConnecting: "Connecting...", statusAuth: "Authorizing with Telegram...", statusReady: "Ready", statusNeedProfile: "Complete your profile to start swiping", statusNoTelegram: "Open this page inside Telegram Mini App", statusMissingInit: "Open Mini App from Telegram menu button. Direct link is not supported.", statusMatch: "🎉 It's a match!", noProfiles: "No more profiles yet. Try later.", noMatches: "No matches yet.", noMessages: "No messages yet.", noGifts: "No gifts yet.", unknownCity: "Unknown", noBio: "No bio", chatWith: "Chat with", you: "You", giftsReceivedCount: "🎁 Gifts received", likesNotice: "You have a like. Open Mini App and check who did it.", giftFrom: "from", partnerAgeFrom: "Partner age from", partnerAgeTo: "Partner age to", giftSent: "Gift sent" },
  zh: { title: "💕 约会 MVP", share: "分享", profile: "完善资料", swipe: "滑动", matches: "匹配", settings: "设置", receivedGifts: "收到的礼物", myProfile: "我的资料", pass: "⬅️ 跳过", like: "❤️ 喜欢", send: "发送", statusConnecting: "连接中...", statusAuth: "正在通过 Telegram 授权...", statusReady: "已就绪", statusNeedProfile: "请先完善资料开始匹配", statusNoTelegram: "请在 Telegram Mini App 中打开", statusMissingInit: "请从 Telegram 菜单按钮打开 Mini App，不支持直接链接。", statusMatch: "🎉 匹配成功！", noProfiles: "暂时没有更多用户。", noMatches: "暂无匹配。", noMessages: "暂无消息。", noGifts: "暂无礼物。", unknownCity: "未知", noBio: "暂无简介", chatWith: "与以下用户聊天", you: "你", giftsReceivedCount: "🎁 收到礼物", likesNotice: "有人喜欢你，打开 Mini App 查看是谁。", giftFrom: "来自", partnerAgeFrom: "伴侣年龄从", partnerAgeTo: "伴侣年龄到", giftSent: "礼物已发送" },
  hi: { title: "💕 डेटिंग MVP", share: "शेयर", profile: "प्रोफाइल पूरी करें", swipe: "स्वाइप", matches: "मैच", settings: "सेटिंग्स", receivedGifts: "मिले हुए गिफ्ट", myProfile: "मेरी प्रोफाइल", pass: "⬅️ छोड़ें", like: "❤️ लाइक", send: "भेजें", statusConnecting: "कनेक्ट हो रहा है...", statusAuth: "Telegram से ऑथराइज़ हो रहा है...", statusReady: "तैयार", statusNeedProfile: "स्वाइप शुरू करने से पहले प्रोफाइल पूरी करें", statusNoTelegram: "इसे Telegram Mini App के अंदर खोलें", statusMissingInit: "Mini App को Telegram मेन्यू बटन से खोलें। डायरेक्ट लिंक समर्थित नहीं है।", statusMatch: "🎉 मैच हो गया!", noProfiles: "अभी और प्रोफाइल नहीं हैं।", noMatches: "अभी कोई मैच नहीं।", noMessages: "अभी कोई संदेश नहीं।", noGifts: "अभी कोई गिफ्ट नहीं।", unknownCity: "अज्ञात", noBio: "कोई बायो नहीं", chatWith: "चैट करें", you: "आप", giftsReceivedCount: "🎁 प्राप्त गिफ्ट", likesNotice: "आपको लाइक आया है, Mini App में जाकर देखें किसने किया।", giftFrom: "से", partnerAgeFrom: "पार्टनर उम्र से", partnerAgeTo: "पार्टनर उम्र तक", giftSent: "गिफ्ट भेजा गया" },
  es: { title: "💕 Dating MVP", share: "Compartir", profile: "Completa tu perfil", swipe: "Deslizar", matches: "Matches", settings: "Ajustes", receivedGifts: "Regalos recibidos", myProfile: "Mi perfil", pass: "⬅️ Pasar", like: "❤️ Me gusta", send: "Enviar", statusConnecting: "Conectando...", statusAuth: "Autorizando con Telegram...", statusReady: "Listo", statusNeedProfile: "Completa tu perfil para empezar", statusNoTelegram: "Abre esta página dentro de Telegram Mini App", statusMissingInit: "Abre Mini App desde el botón del menú de Telegram. El enlace directo no funciona.", statusMatch: "🎉 ¡Es un match!", noProfiles: "No hay más perfiles por ahora.", noMatches: "Aún no hay matches.", noMessages: "Aún no hay mensajes.", noGifts: "Aún no hay regalos.", unknownCity: "Desconocido", noBio: "Sin bio", chatWith: "Chat con", you: "Tú", giftsReceivedCount: "🎁 Regalos recibidos", likesNotice: "Tienes un like. Entra en Mini App para ver quién fue.", giftFrom: "de", partnerAgeFrom: "Edad pareja desde", partnerAgeTo: "Edad pareja hasta", giftSent: "Regalo enviado" },
  ru: { title: "💕 Dating MVP", share: "Поделиться", profile: "Заполните профиль", swipe: "Свайпы", matches: "Матчи", settings: "Настройки", receivedGifts: "Полученные подарки", myProfile: "Мой профиль", pass: "⬅️ Пропустить", like: "❤️ Лайк", send: "Отправить", statusConnecting: "Подключение...", statusAuth: "Авторизация через Telegram...", statusReady: "Готово", statusNeedProfile: "Заполните профиль, чтобы начать свайпать", statusNoTelegram: "Откройте страницу внутри Telegram Mini App", statusMissingInit: "Откройте Mini App через кнопку меню Telegram. Прямой URL не поддерживается.", statusMatch: "🎉 Это матч!", noProfiles: "Пока нет новых анкет.", noMatches: "Пока нет матчей.", noMessages: "Пока нет сообщений.", noGifts: "Пока нет подарков.", unknownCity: "Не указан", noBio: "Без описания", chatWith: "Чат с", you: "Вы", giftsReceivedCount: "🎁 Получено подарков", likesNotice: "У тебя есть лайк, зайди проверить кто это сделал.", giftFrom: "от", partnerAgeFrom: "Возраст партнера от", partnerAgeTo: "Возраст партнера до", giftSent: "Подарок отправлен" },
};

const statusEl = document.getElementById("status");
const profileSection = document.getElementById("profileSection");
const swipeSection = document.getElementById("swipeSection");
const settingsSection = document.getElementById("settingsSection");
const profileForm = document.getElementById("profileForm");
const settingsForm = document.getElementById("settingsForm");
const profilePhotoInput = document.getElementById("profilePhotoInput");
const settingsPhotoInput = document.getElementById("settingsPhotoInput");
const candidateCard = document.getElementById("candidateCard");
const matchesList = document.getElementById("matchesList");
const chatSection = document.getElementById("chatSection");
const chatTitle = document.getElementById("chatTitle");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const giftsList = document.getElementById("giftsList");
const myProfileSection = document.getElementById("myProfileSection");
const myProfileCard = document.getElementById("myProfileCard");
const languageSelect = document.getElementById("languageSelect");
const citySuggestions = document.getElementById("citySuggestions");

function t(key, vars = {}) {
  const dict = i18n[state.language] || i18n.en;
  let text = dict[key] || i18n.en[key] || key;
  for (const [k, v] of Object.entries(vars)) text = text.replace(`{${k}}`, String(v));
  return text;
}

function applyI18n() {
  document.querySelector(".topbar h1").textContent = t("title");
  document.getElementById("shareBtn").textContent = t("share");
  document.getElementById("profileTitle").textContent = t("profile");
  document.getElementById("swipeTitle").textContent = t("swipe");
  document.getElementById("myProfileTitle").textContent = t("myProfile");
  document.getElementById("settingsTitle").textContent = t("settings");
  document.getElementById("matchesTitle").textContent = t("matches");
  document.getElementById("receivedGiftsTitle").textContent = t("receivedGifts");
  document.getElementById("dislikeBtn").textContent = t("pass");
  document.getElementById("likeBtn").textContent = t("like");
  document.getElementById("sendBtn").textContent = t("send");
  settingsForm.querySelector('input[name="min_age"]').placeholder = t("partnerAgeFrom");
  settingsForm.querySelector('input[name="max_age"]').placeholder = t("partnerAgeTo");
}

function setStatus(message) { statusEl.textContent = message; }

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "API error");
  return payload;
}

async function uploadPhoto(file) {
  if (!file) return null;
  const form = new FormData();
  form.append("file", file);
  const data = await api("/api/profile/photo-upload", { method: "POST", body: form });
  return data.photo_url;
}

function renderCandidate(candidate) {
  state.currentCandidate = candidate;
  if (!candidate) {
    candidateCard.textContent = t("noProfiles");
    return;
  }
  const photo = candidate.photo_id ? `<img src="${candidate.photo_id}" alt="${candidate.name}" class="profileImage" />` : "";
  candidateCard.innerHTML = `${photo}<h3>${candidate.name}, ${candidate.age}</h3><p>📍 ${candidate.city || t("unknownCity")}</p><p>${candidate.bio || t("noBio")}</p>`;
}

async function loadCandidate() {
  const data = await api("/api/feed/next");
  renderCandidate(data.candidate);
}

async function doSwipe(action) {
  if (!state.currentCandidate) return;
  const data = await api("/api/swipe", { method: "POST", body: JSON.stringify({ to_user_id: state.currentCandidate.user_id, action }) });
  if (data.match) setStatus(t("statusMatch"));
  renderCandidate(data.next_candidate);
  await loadMatches();
}

async function pickGiftCode() {
  const tg = window.Telegram?.WebApp;
  if (tg?.showPopup) {
    return new Promise((resolve) => {
      tg.showPopup(
        {
          title: "Gift",
          message: "Choose gift",
          buttons: [
            { id: "rose", type: "default", text: "🌹" },
            { id: "heart", type: "default", text: "💖" },
            { id: "cake", type: "default", text: "🎂" },
            { id: "cancel", type: "close", text: "Cancel" },
          ],
        },
        (id) => resolve(id === "cancel" ? null : id)
      );
    });
  }
  return "rose";
}

async function sendGiftTo(userId) {
  const giftCode = await pickGiftCode();
  if (!giftCode) return;
  await api("/api/gifts/send", { method: "POST", body: JSON.stringify({ to_user_id: userId, gift_code: giftCode, gift_message: "" }) });
  setStatus(t("giftSent"));
  await loadReceivedGifts();
}

function renderMatches(matches) {
  if (!matches.length) {
    matchesList.textContent = t("noMatches");
    return;
  }
  matchesList.innerHTML = "";
  for (const match of matches) {
    const row = document.createElement("div");
    row.className = "matchRow";

    const chatBtn = document.createElement("button");
    chatBtn.type = "button";
    chatBtn.className = "matchChatBtn";
    chatBtn.textContent = `💬 ${match.name}, ${match.age}`;
    chatBtn.addEventListener("click", () => openChat(match.user_id, match.name));

    const giftBtn = document.createElement("button");
    giftBtn.type = "button";
    giftBtn.className = "giftIconBtn";
    giftBtn.title = "Send gift";
    giftBtn.textContent = "🎁";
    giftBtn.addEventListener("click", () => sendGiftTo(match.user_id));

    row.append(chatBtn, giftBtn);
    matchesList.appendChild(row);
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
  chatTitle.textContent = `${t("chatWith")} ${name}`;
  const data = await api(`/api/chat/${otherUserId}`);
  if (!data.messages.length) {
    chatMessages.textContent = t("noMessages");
    return;
  }
  chatMessages.innerHTML = data.messages.map((m) => `<p><strong>${m.from_user_id === otherUserId ? name : t("you")}:</strong> ${m.message}</p>`).join("");
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage() {
  if (!state.selectedMatchId) return;
  const text = chatInput.value.trim();
  if (!text) return;
  await api(`/api/chat/${state.selectedMatchId}`, { method: "POST", body: JSON.stringify({ message: text }) });
  chatInput.value = "";
  await openChat(state.selectedMatchId, state.selectedMatchName);
}

async function loadReceivedGifts() {
  const data = await api("/api/gifts/received");
  if (!data.gifts.length) {
    giftsList.textContent = t("noGifts");
    renderMyProfile(state.me, data.gifts);
    return;
  }
  giftsList.innerHTML = data.gifts.map((g) => `<div>🎁 ${g.gift_name} ${t("giftFrom")} ${g.from_name}</div>`).join("");
  renderMyProfile(state.me, data.gifts);
}

function renderMyProfile(me, gifts) {
  if (!me || !me.user) {
    myProfileSection.classList.add("hidden");
    return;
  }
  myProfileSection.classList.remove("hidden");
  const user = me.user;
  const photo = user.photo_id ? `<img src="${user.photo_id}" alt="${user.name}" class="profileImage" />` : "";
  myProfileCard.innerHTML = `${photo}<h3>${user.name}, ${user.age}</h3><p>📍 ${user.city || t("unknownCity")}</p><p>${user.bio || t("noBio")}</p><p><strong>${t("giftsReceivedCount")}:</strong> ${gifts.length}</p><p><strong>${t("partnerAgeFrom")}:</strong> ${user.min_age} · <strong>${t("partnerAgeTo")}:</strong> ${user.max_age}</p>`;
}

function fillSettingsForm(user) {
  if (!user) return;
  settingsForm.name.value = user.name || "";
  settingsForm.age.value = user.age || "";
  settingsForm.city.value = user.city || "";
  settingsForm.bio.value = user.bio || "";
  settingsForm.min_age.value = user.min_age || 18;
  settingsForm.max_age.value = user.max_age || 100;
}

function validateAges(age, minAge, maxAge) {
  if (!Number.isFinite(age) || age < 18) return false;
  if (!Number.isFinite(minAge) || minAge < 18) return false;
  if (!Number.isFinite(maxAge) || maxAge < 18) return false;
  if (minAge > maxAge) return false;
  return true;
}

async function loadCitySuggestions(query) {
  const normalized = query.trim();
  if (normalized.length < 3) {
    citySuggestions.innerHTML = "";
    return;
  }
  const data = await api(`/api/cities/suggest?query=${encodeURIComponent(normalized)}`);
  citySuggestions.innerHTML = "";
  for (const city of data.cities || []) {
    const option = document.createElement("option");
    option.value = city;
    citySuggestions.appendChild(option);
  }
}

async function submitProfile(event) {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const photoUrl = await uploadPhoto(profilePhotoInput.files[0]);
  const payload = Object.fromEntries(formData.entries());
  payload.age = Number(payload.age);
  payload.min_age = 18;
  payload.max_age = 100;
  if (!validateAges(payload.age, payload.min_age, payload.max_age)) {
    setStatus("Age must be 18+");
    return;
  }
  if (photoUrl) payload.photo_id = photoUrl;
  await api("/api/profile", { method: "POST", body: JSON.stringify(payload) });
  state.me = await api("/api/me");
  fillSettingsForm(state.me.user);
  profileSection.classList.add("hidden");
  swipeSection.classList.remove("hidden");
  await loadCandidate();
  await loadMatches();
  await loadReceivedGifts();
}

async function submitSettings(event) {
  event.preventDefault();
  const formData = new FormData(settingsForm);
  const payload = Object.fromEntries(formData.entries());
  payload.age = Number(payload.age);
  payload.min_age = Number(payload.min_age);
  payload.max_age = Number(payload.max_age);
  if (!validateAges(payload.age, payload.min_age, payload.max_age)) {
    setStatus("Age must be 18+ and partner range must be valid");
    return;
  }
  payload.gender = state.me.user.gender;
  payload.looking_for = state.me.user.looking_for;
  const photoUrl = await uploadPhoto(settingsPhotoInput.files[0]);
  payload.photo_id = photoUrl || state.me.user.photo_id || null;
  await api("/api/profile", { method: "POST", body: JSON.stringify(payload) });
  state.me = await api("/api/me");
  settingsSection.classList.add("hidden");
  await loadCandidate();
  await loadReceivedGifts();
}

async function shareBot() {
  const data = await api("/api/share-link");
  if (window.Telegram?.WebApp?.openTelegramLink) window.Telegram.WebApp.openTelegramLink(data.share_url);
  else window.open(data.share_url, "_blank");
}

function getTelegramInitData(tg) {
  if (tg?.initData && tg.initData.includes("hash=")) return tg.initData;
  const fromQuery = new URLSearchParams(window.location.search).get("tgWebAppData");
  if (fromQuery) {
    const decoded = decodeURIComponent(fromQuery);
    if (decoded.includes("hash=")) return decoded;
  }
  return "";
}

function setupSwipeGestures() {
  let startX = 0;
  candidateCard.addEventListener("touchstart", (e) => { startX = e.changedTouches[0].clientX; }, { passive: true });
  candidateCard.addEventListener("touchend", (e) => {
    const deltaX = e.changedTouches[0].clientX - startX;
    if (deltaX > 60) doSwipe("like");
    if (deltaX < -60) doSwipe("dislike");
  }, { passive: true });
}

function setupCityAutocomplete() {
  const cityInputs = [
    profileForm.querySelector('input[name="city"]'),
    settingsForm.querySelector('input[name="city"]'),
  ];
  for (const cityInput of cityInputs) {
    cityInput.addEventListener("input", () => {
      loadCitySuggestions(cityInput.value).catch(() => {});
    });
  }
}

async function loadLikesHint() {
  const data = await api("/api/likes/inbox-count");
  if (data.count > 0) setStatus(t("likesNotice"));
}

async function init() {
  try {
    applyI18n();
    setStatus(t("statusConnecting"));
    const tg = window.Telegram?.WebApp;
    if (!tg) { setStatus(t("statusNoTelegram")); return; }
    tg.ready();
    tg.expand();
    const initData = getTelegramInitData(tg);
    if (!initData) { setStatus(t("statusMissingInit")); return; }

    setStatus(t("statusAuth"));
    const auth = await api("/api/auth/telegram", { method: "POST", body: JSON.stringify({ initData }) });
    state.token = auth.token;
    state.me = await api("/api/me");

    if (!state.me.profile_complete) {
      setStatus(t("statusNeedProfile"));
      profileSection.classList.remove("hidden");
      swipeSection.classList.add("hidden");
    } else {
      setStatus(t("statusReady"));
      profileSection.classList.add("hidden");
      swipeSection.classList.remove("hidden");
      await loadCandidate();
      fillSettingsForm(state.me.user);
    }

    await loadMatches();
    await loadReceivedGifts();
    await loadLikesHint();
  } catch (error) {
    setStatus(`Error: ${error.message}`);
  }
}

document.getElementById("likeBtn").addEventListener("click", () => doSwipe("like"));
document.getElementById("dislikeBtn").addEventListener("click", () => doSwipe("dislike"));
document.getElementById("sendBtn").addEventListener("click", sendMessage);
document.getElementById("shareBtn").addEventListener("click", shareBot);
document.getElementById("settingsBtn").addEventListener("click", () => settingsSection.classList.toggle("hidden"));
document.getElementById("closeSettingsBtn").addEventListener("click", () => settingsSection.classList.add("hidden"));
profileForm.addEventListener("submit", submitProfile);
settingsForm.addEventListener("submit", submitSettings);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
languageSelect.value = state.language;
languageSelect.addEventListener("change", () => {
  state.language = languageSelect.value;
  localStorage.setItem("miniapp_lang", state.language);
  init();
});
setupSwipeGestures();
setupCityAutocomplete();
init();
