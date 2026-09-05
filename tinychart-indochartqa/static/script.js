const imageInput = document.getElementById("imageInput");
const previewImage = document.getElementById("previewImage");
const emptyPreview = document.getElementById("emptyPreview");

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");

const chatBox = document.getElementById("chatBox");


// ==========================
// Preview Image
// ==========================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    previewImage.src = URL.createObjectURL(file);

    previewImage.classList.remove("d-none");

    emptyPreview.classList.add("d-none");

});


// ==========================
// Add Chat Bubble
// ==========================

function addUserMessage(message){

    chatBox.innerHTML += `
        <div class="user-message">
            <div class="user-bubble">
                ${message}
            </div>
        </div>
    `;

    scrollToBottom();

}

function addBotMessage(pot, answer){

    // Hapus tag <comment> dan <step>
    const potText = pot
        .replace(/<comment>/g, "")
        .replace(/<\/comment>/g, "")
        .replace(/<step>/g, "")
        .replace(/<\/step>/g, "");

    // Answer hanya ditampilkan jika ada
    let answerHTML = "";

    if (answer !== null && answer !== undefined) {
        answerHTML = `
            <div class="final-answer">
                <strong>Answer:</strong>
                <span class="answer-text"></span>
            </div>
        `;
    }

    chatBox.innerHTML += `
        <div class="bot-message">
            <div class="bot-bubble">

                <pre class="pot-code"></pre>

                ${answerHTML}

            </div>
        </div>
    `;

    const botBubble = chatBox.lastElementChild.querySelector(".bot-bubble");

    // Tampilkan PoT tanpa tag XML
    botBubble.querySelector(".pot-code").textContent = potText;

    // Isi Answer jika memang ada
    if (answer !== null && answer !== undefined) {
        botBubble.querySelector(".answer-text").textContent = answer;
    }

    scrollToBottom();

}

// ==========================
// Loading Bubble
// ==========================

function showLoading(){

    chatBox.innerHTML += `
        <div class="bot-message" id="loadingBubble">

            <div class="bot-bubble loading">

                TinyChart is thinking...

            </div>

        </div>
    `;

    scrollToBottom();

}


function removeLoading(){

    const loading = document.getElementById("loadingBubble");

    if(loading){

        loading.remove();

    }

}


// ==========================
// Scroll Chat
// ==========================

function scrollToBottom(){

    chatBox.scrollTop = chatBox.scrollHeight;

}


// ==========================
// Ask Question
// ==========================

async function askQuestion(){

    const image = imageInput.files[0];
    const question = questionInput.value.trim();

    if(!image){

        alert("Please upload a chart image.");

        return;

    }

    if(question === ""){

        alert("Please enter a question.");

        return;

    }

    addUserMessage(question);

    showLoading();

    questionInput.value = "";

    askButton.disabled = true;

    const formData = new FormData();

    formData.append("image", image);
    formData.append("question", question);

    try{

        const response = await fetch("/predict",{

            method:"POST",

            body:formData

        });

        const data = await response.json();

        removeLoading();

        addBotMessage(data.pot, data.answer);

    }

    catch(error){

        removeLoading();

        addBotMessage("An error occurred.");

        console.error(error);

    }

    askButton.disabled = false;

}


// ==========================
// Button
// ==========================

askButton.addEventListener("click", askQuestion);


// ==========================
// Enter Key
// ==========================

questionInput.addEventListener("keypress", function(e){

    if(e.key === "Enter"){

        askQuestion();

    }

});