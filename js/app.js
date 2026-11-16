const chatForm = document.querySelector("[data-chat-form]");

if (chatForm) {
  const input = chatForm.querySelector("textarea");
  const messageList = document.querySelector("[data-message-list]");
  const welcome = document.querySelector("[data-welcome]");
  const sidebar = document.querySelector("#chat-sidebar");
  const scrim = document.querySelector(".sidebar-scrim");

  const closeSidebar = () => {
    sidebar?.classList.remove("is-open");
    scrim?.classList.remove("is-visible");
  };

  const addMessage = (role, text) => {
    const message = document.createElement("article");
    message.className = `message message-${role}`;

    const label = document.createElement("span");
    label.className = "message-role";
    label.textContent = role === "user" ? "You" : "Assistant";

    const content = document.createElement("p");
    content.className = "message-text";
    content.textContent = text;

    message.append(label, content);
    messageList.append(message);
    message.scrollIntoView({ behavior: "smooth", block: "nearest" });
  };

  const sendMessage = (text) => {
    const message = text.trim();
    if (!message) return;

    welcome.hidden = true;
    addMessage("user", message);
    addMessage("assistant", "Please open the live assistant from the home page to ask a question.");
    input.value = "";
    input.style.height = "auto";
  };

  chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(input.value);
    input.focus();
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 140)}px`;
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      chatForm.requestSubmit();
    }
  });

  document.querySelectorAll("[data-prompt]").forEach((button) => {
    button.addEventListener("click", () => sendMessage(button.dataset.prompt));
  });

  document.querySelectorAll("[data-new-chat]").forEach((button) => {
    button.addEventListener("click", () => {
      messageList.replaceChildren();
      welcome.hidden = false;
      input.value = "";
      input.style.height = "auto";
      closeSidebar();
      input.focus();
    });
  });

  document.querySelector("[data-open-sidebar]")?.addEventListener("click", () => {
    sidebar?.classList.add("is-open");
    scrim?.classList.add("is-visible");
  });

  document.querySelectorAll("[data-close-sidebar]").forEach((button) => {
    button.addEventListener("click", closeSidebar);
  });
}