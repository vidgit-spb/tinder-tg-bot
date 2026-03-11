const state = {
  token: null,
  me: null,
  currentCandidate: null,
  selectedMatchId: null,
  selectedMatchName: "",
  language: localStorage.getItem("miniapp_lang") || "en",
};

const i18n = {
  en: {
    title: "💕 Dating MVP",
    share: "Share",
    profile: "Complete profile",
    swipe: "Swipe",
    matches: "Matches",
    receivedGifts: "Received gifts",
    myProfile: "My profile",
    pass: "⬅️ Pass",
    like: "❤️ Like",
    send: "Send",
    sendGift: "Send gift",
    statusConnecting: "Connecting...",
    statusAuth: "Authorizing with Telegram...",
    statusReady: "Ready",
    statusNeedProfile: "Complete your profile to start swiping",
    statusNoTelegram: "Open this page inside Telegram Mini App",
    statusMissingInit: "Open Mini App from Telegram menu button. Direct link is not supported.",
    statusGiftViaBot: "Gift purchase is available in bot menu via Telegram Stars.",
    statusMatch: "🎉 It's a match!",
    noProfiles: "No more profiles yet. Try later.",
    noMatches: "No matches yet.",
    noMessages: "No messages yet.",
    noGifts: "No gifts yet.",
    unknownCity: "Unknown",
    noBio: "No bio",
    chatWith: "Chat with",
    you: "You",
    giftsReceivedCount: "🎁 Gifts received",
    likesNotice: "❤️ You have {count} likes. Open chats and matches now.",
    giftFrom: "from",
  },
  zh: {
    title: "💕 约会 MVP",
    share: "分享",
    profile: "完善资料",
    swipe: "滑动",
    matches: "匹配",
    receivedGifts: "收到的礼物",
    myProfile: "我的资料",
    pass: "⬅️ 跳过",
    like: "❤️ 喜欢",
    send: "发送",
    sendGift: "发送礼物",
    statusConnecting: "连接中...",
    statusAuth: "正在通过 Telegram 授权...",
    statusReady: "已就绪",
    statusNeedProfile: "请先完善资料开始匹配",
    statusNoTelegram: "请在 Telegram Mini App 中打开",
    statusMissingInit: "请从 Telegram 菜单按钮打开 Mini App，不支持直接链接。",
    statusGiftViaBot: "礼物购买请在机器人菜单中使用 Telegram Stars。",
    statusMatch: "🎉 匹配成功！",
    noProfiles: "暂时没有更多用户。",
    noMatches: "暂无匹配。",
    noMessages: "暂无消息。",
    noGifts: "暂无礼物。",
    unknownCity: "未知",
    noBio: "暂无简介",
    chatWith: "与以下用户聊天",
    you: "你",
    giftsReceivedCount: "🎁 收到礼物",
    likesNotice: "❤️ 有 {count} 人喜欢你。快去查看匹配和聊天。",
    giftFrom: "来自",
  },
  hi: {
    title: "💕 डेटिंग MVP",
    share: "शेयर",
    profile: "प्रोफाइल पूरी करें",
    swipe: "स्वाइप",
    matches: "मैच",
    receivedGifts: "मिले हुए गिफ्ट",
    myProfile: "मेरी प्रोफाइल",
    pass: "⬅️ छोड़ें",
    like: "❤️ लाइक",
    send: "भेजें",
    sendGift: "गिफ्ट भेजें",
    statusConnecting: "कनेक्ट हो रहा है...",
    statusAuth: "Telegram से ऑथराइज़ हो रहा है...",
    statusReady: "तैयार",
    statusNeedProfile: "स्वाइप शुरू करने से पहले प्रोफाइल पूरी करें",
    statusNoTelegram: "इसे Telegram Mini App के अंदर खोलें",
    statusMissingInit: "Mini App को Telegram मेन्यू बटन से खोलें। डायरेक्ट लिंक समर्थित नहीं है।",
    statusGiftViaBot: "गिफ्ट खरीद बॉट मेन्यू में Telegram Stars से उपलब्ध है।",
    statusMatch: "🎉 मैच हो गया!",
    noProfiles: "अभी और प्रोफाइल नहीं हैं।",
    noMatches: "अभी कोई मैच नहीं।",
    noMessages: "अभी कोई संदेश नहीं।",
    noGifts: "अभी कोई गिफ्ट नहीं।",
    unknownCity: "अज्ञात",
    noBio: "कोई बायो नहीं",
    chatWith: "चैट करें",
    you: "आप",
    giftsReceivedCount: "🎁 प्राप्त गिफ्ट",
    likesNotice: "❤️ आपको {count} लाइक मिले हैं। अभी Mini App खोलकर देखें।",
    giftFrom: "से",
  },
  es: {
    title: "💕 Dating MVP",
    share: "Compartir",
    profile: "Completa tu perfil",
    swipe: "Deslizar",
    matches: "Matches",
    receivedGifts: "Regalos recibidos",
    myProfile: "Mi perfil",
    pass: "⬅️ Pasar",
    like: "❤️ Me gusta",
    send: "Enviar",
    sendGift: "Enviar regalo",
    statusConnecting: "Conectando...",
    statusAuth: "Autorizando con Telegram...",
    statusReady: "Listo",
    statusNeedProfile: "Completa tu perfil para empezar",
    statusNoTelegram: "Abre esta página dentro de Telegram Mini App",
    statusMissingInit: "Abre Mini App desde el botón del menú de Telegram. El enlace directo no funciona.",
    statusGiftViaBot: "La compra de regalos está en el menú del bot con Telegram Stars.",
    statusMatch: "🎉 ¡Es un match!",
    noProfiles: "No hay más perfiles por ahora.",
    noMatches: "Aún no hay matches.",
    noMessages: "Aún no hay mensajes.",
    noGifts: "Aún no hay regalos.",
    unknownCity: "Desconocido",
    noBio: "Sin bio",
    chatWith: "Chat con",
    you: "Tú",
    giftsReceivedCount: "🎁 Regalos recibidos",
    likesNotice: "❤️ Tienes {count} likes. Abre matches y chat ahora.",
    giftFrom: "de",
  },
  ru: {
    title: "💕 Dating MVP",
    share: "Поделиться",
    profile: "Заполните профиль",
    swipe: "Свайпы",
    matches: "Матчи",
    receivedGifts: "Полученные подарки",
    myProfile: "Мой профиль",
    pass: "⬅️ Пропустить",
    like: "❤️ Лайк",
    send: "Отправить",
    sendGift: "Отправить подарок",
    statusConnecting: "Подключение...",
    statusAuth: "Авторизация через Telegram...",
    statusReady: "Готово",
    statusNeedProfile: "Заполните профиль, чтобы начать свайпать",
    statusNoTelegram: "Откройте страницу внутри Telegram Mini App",
    statusMissingInit: "Откройте Mini App через кнопку меню Telegram. Прямой URL не поддерживается.",
    statusGiftViaBot: "Покупка подарка доступна в меню бота за Telegram Stars.",
    statusMatch: "🎉 Это матч!",
    noProfiles: "Пока нет новых анкет.",
    noMatches: "Пока нет матчей.",
    noMessages: "Пока нет сообщений.",
    noGifts: "Пока нет подарков.",
    unknownCity: "Не указан",
    noBio: "Без описания",
    chatWith: "Чат с",
    you: "Вы",
    giftsReceivedCount: "🎁 Получено подарков",
    likesNotice: "❤️ Вас лайкнули: {count}. Зайдите в Mini App и проверьте матчи.",
    giftFrom: "от",
  },
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
const myProfileSection = document.getElementById("myProfileSection");
const myProfileCard = document.getElementById("myProfileCard");
const languageSelect = document.getElementById("languageSelect");

function t(key, vars = {}) {
  const dict = i18n[state.language] || i18n.en;
  let text = dict[key] || i18n.en[key] || key;
  for (const [k, v] of Object.entries(vars)) {
    text = text.replace(`{${k}}`, String(v));
  }
  return text;
}

function applyI18n() {
  document.querySelector(".topbar h1").textContent = t("title");
  document.getElementById("shareBtn").textContent = t("share");
  document.querySelector("#profileSection h2").textContent = t("profile");
  document.querySelector("#swipeSection h2").textContent = t("swipe");
  document.querySelector("#myProfileSection h2").textContent = t("myProfile");
  document.querySelectorAll(".panel h2")[2].textContent = t("matches");
  document.querySelectorAll(".panel h2")[4].textContent = t("receivedGifts");
  document.getElementById("dislikeBtn").textContent = t("pass");
  document.getElementById("likeBtn").textContent = t("like");
  document.getElementById("sendBtn").textContent = t("send");
  document.getElementById("giftBtn").textContent = t("sendGift");
}

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
    candidateCard.textContent = t("noProfiles");
    return;
  }
  candidateCard.innerHTML = `
    <h3>${candidate.name}, ${candidate.age}</h3>
    <p>📍 ${candidate.city || t("unknownCity")}</p>
    <p>${candidate.bio || t("noBio")}</p>
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
    body: JSON.stringify({ to_user_id: state.currentCandidate.user_id, action }),
  });
  if (data.match) setStatus(t("statusMatch"));
  renderCandidate(data.next_candidate);
  await loadMatches();
}

function renderMatches(matches) {
  if (!matches.length) {
    matchesList.textContent = t("noMatches");
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
  chatTitle.textContent = `${t("chatWith")} ${name}`;
  const data = await api(`/api/chat/${otherUserId}`);
  if (!data.messages.length) {
    chatMessages.textContent = t("noMessages");
    return;
  }
  chatMessages.innerHTML = data.messages
    .map((m) => `<p><strong>${m.from_user_id === otherUserId ? name : t("you")}:</strong> ${m.message}</p>`)
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
  try {
    await api("/api/gifts/send", {
      method: "POST",
      body: JSON.stringify({ to_user_id: state.selectedMatchId, gift_code: giftCode, gift_message: "" }),
    });
    await loadReceivedGifts();
  } catch {
    setStatus(t("statusGiftViaBot"));
  }
}

async function loadReceivedGifts() {
  const data = await api("/api/gifts/received");
  if (!data.gifts.length) {
    giftsList.textContent = t("noGifts");
    renderMyProfile(state.me, data.gifts);
    return;
  }
  giftsList.innerHTML = data.gifts
    .map((g) => `<div>🎁 ${g.gift_name} ${t("giftFrom")} ${g.from_name}</div>`)
    .join("");
  renderMyProfile(state.me, data.gifts);
}

function renderMyProfile(me, gifts) {
  if (!me || !me.user) {
    myProfileSection.classList.add("hidden");
    return;
  }
  myProfileSection.classList.remove("hidden");
  const user = me.user;
  myProfileCard.innerHTML = `
    <h3>${user.name}, ${user.age}</h3>
    <p>📍 ${user.city || t("unknownCity")}</p>
    <p>${user.bio || t("noBio")}</p>
    <p><strong>${t("giftsReceivedCount")}:</strong> ${gifts.length}</p>
  `;
}

async function submitProfile(event) {
  event.preventDefault();
  const formData = new FormData(profileForm);
  const payload = Object.fromEntries(formData.entries());
  payload.age = Number(payload.age);
  await api("/api/profile", { method: "POST", body: JSON.stringify(payload) });
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

function getTelegramInitData(tg) {
  if (tg?.initData && tg.initData.includes("hash=")) return tg.initData;
  const fromQuery = new URLSearchParams(window.location.search).get("tgWebAppData");
  if (fromQuery) {
    const decoded = decodeURIComponent(fromQuery);
    if (decoded.includes("hash=")) return decoded;
  }
  return "";
}

async function loadLikesHint() {
  const data = await api("/api/likes/inbox-count");
  if (data.count > 0) {
    setStatus(t("likesNotice", { count: data.count }));
  }
}

async function init() {
  try {
    applyI18n();
    setStatus(t("statusConnecting"));
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setStatus(t("statusNoTelegram"));
      return;
    }
    tg.ready();
    tg.expand();

    const initData = getTelegramInitData(tg);
    if (!initData) {
      setStatus(t("statusMissingInit"));
      return;
    }

    setStatus(t("statusAuth"));
    const auth = await api("/api/auth/telegram", {
      method: "POST",
      body: JSON.stringify({ initData }),
    });

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
document.getElementById("giftBtn").addEventListener("click", sendGift);
document.getElementById("shareBtn").addEventListener("click", shareBot);
profileForm.addEventListener("submit", submitProfile);
languageSelect.value = state.language;
languageSelect.addEventListener("change", () => {
  state.language = languageSelect.value;
  localStorage.setItem("miniapp_lang", state.language);
  init();
});

init();
