/* =====================================================
   CHAT SYSTEM
===================================================== */

function sendMessage(customMessage = null){

  const input = document.getElementById("chatInput");
  const message = customMessage || input.value.trim();

  if(!message) return;

  const chatBox = document.getElementById("chatBox");

  const empty = chatBox.querySelector(".empty");
  if(empty) empty.remove();

  // USER MESSAGE
  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble user";
  userBubble.innerText = message;

  chatBox.appendChild(userBubble);
  chatBox.scrollTop = chatBox.scrollHeight;

  input.value = "";

  // LOADING MESSAGE
  const loadingBubble = document.createElement("div");
  loadingBubble.className = "chat-bubble bot";
  loadingBubble.innerText = "Analyzing traffic data...";

  chatBox.appendChild(loadingBubble);
  chatBox.scrollTop = chatBox.scrollHeight;

  fetch("/chat",{
    method:"POST",
    headers:{
      "Content-Type":"application/json"
    },
    body: JSON.stringify({
      message: message
    })
  })
  .then(res => res.json())
  .then(data => {

    loadingBubble.innerHTML = formatAIMessage(data.reply);
    chatBox.scrollTop = chatBox.scrollHeight;

  })
  .catch(err => {

    loadingBubble.innerText =
      "⚠️ AI assistant could not generate a response.";

    console.error(err);

  });

}


/* =====================================================
   AI MESSAGE FORMAT
===================================================== */

function formatAIMessage(text){

  if(!text) return "";

  let formatted = text;

  formatted = formatted.replace(/\n/g,"<br>");
  formatted = formatted.replace(/\*\*(.*?)\*\*/g,"<strong>$1</strong>");
  formatted = formatted.replace(/•/g,"<br>• ");

  return formatted;

}


/* =====================================================
   HELPER
===================================================== */

function escapeHtml(str){

  return str
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;");

}


/* =====================================================
   ENTER KEY SUPPORT
===================================================== */

document.addEventListener("DOMContentLoaded",()=>{

  const input = document.getElementById("chatInput");

  if(input){
    input.addEventListener("keypress", function(e){
      if(e.key === "Enter"){
        sendMessage();
      }
    });
  }

});