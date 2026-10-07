document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // GET HTML ELEMENTS
    // =========================================================

    const askButton = document.getElementById("askBtn");
    const caseNameInput = document.getElementById("caseName");
    const questionInput = document.getElementById("question");

    const answerSection = document.getElementById("answerSection");
    const answerText = document.getElementById("answerText");

    const modelName = document.getElementById("modelName");
    const sourceCount = document.getElementById("sourceCount");
    const sourcesContainer = document.getElementById("sourcesContainer");


    // =========================================================
    // CHECK WHETHER REQUIRED ELEMENTS EXIST
    // =========================================================

    if (!askButton) {
        console.error("ERROR: askBtn not found.");
        return;
    }

    if (!caseNameInput || !questionInput) {
        console.error("ERROR: Input fields not found.");
        return;
    }


    // =========================================================
    // ASK LEGAL QUESTION
    // =========================================================

    async function askLegalQuestion() {

        const caseName = caseNameInput.value.trim();
        const question = questionInput.value.trim();


        // -----------------------------------------------------
        // VALIDATION
        // -----------------------------------------------------

        if (!caseName) {
            alert("Please enter a case name.");
            caseNameInput.focus();
            return;
        }

        if (!question) {
            alert("Please enter your question.");
            questionInput.focus();
            return;
        }


        // -----------------------------------------------------
        // BUTTON LOADING STATE
        // -----------------------------------------------------

        askButton.disabled = true;

        const buttonText = askButton.querySelector(".button-text");

        if (buttonText) {
            buttonText.textContent = "SEARCHING...";
        }


        // Hide previous answer while searching

        if (answerSection) {
            answerSection.classList.add("hidden");
        }


        try {

            console.log("Sending request to /ask...");
            console.log("Case:", caseName);
            console.log("Question:", question);


            // =================================================
            // SEND REQUEST TO FLASK
            // =================================================

            const response = await fetch("/ask", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    case_name: caseName,
                    question: question

                })

            });


            console.log("Response status:", response.status);


            // =================================================
            // GET RESPONSE
            // =================================================

            const data = await response.json();


            console.log("Backend response:", data);


            // =================================================
            // HANDLE BACKEND ERROR
            // =================================================

            if (!response.ok) {

                throw new Error(
                    data.error ||
                    data.message ||
                    "The server returned an error."
                );

            }


            // =================================================
            // CHECK ANSWER
            // =================================================

            if (!data.answer) {

                throw new Error(
                    "The server returned successfully, but no answer was received."
                );

            }


            // =================================================
            // DISPLAY ANSWER
            // =================================================

            if (answerText) {

                answerText.textContent = data.answer;

            }


            // =================================================
            // DISPLAY MODEL
            // =================================================

            if (modelName) {

                modelName.textContent =
                    data.model || "Gemini RAG";

            }


            // =================================================
            // DISPLAY SOURCES
            // =================================================

            if (sourcesContainer) {

                sourcesContainer.innerHTML = "";

            }


            const sources = Array.isArray(data.sources)
                ? data.sources
                : [];


            if (sourceCount) {

                sourceCount.textContent =
                    `${sources.length} Source${sources.length === 1 ? "" : "s"}`;

            }


            // =================================================
            // CREATE SOURCE CARDS
            // =================================================

            if (sourcesContainer && sources.length > 0) {

                sources.forEach((source, index) => {

                    const sourceCard =
                        document.createElement("div");

                    sourceCard.className = "source-card";


                    // Source text

                    const sourceText =
                        source.text ||
                        source.content ||
                        source.chunk ||
                        "Source text unavailable.";


                    // Similarity

                    let similarity = "N/A";

                    if (
                        source.similarity !== undefined &&
                        source.similarity !== null
                    ) {

                        similarity =
                            Number(source.similarity).toFixed(4);

                    }


                    sourceCard.innerHTML = `

                        <div class="source-card-header">

                            <h4>
                                Source ${index + 1}
                            </h4>

                            <span class="source-similarity">
                                Similarity: ${similarity}
                            </span>

                        </div>

                        <p>
                            ${escapeHtml(sourceText)}
                        </p>

                    `;


                    sourcesContainer.appendChild(sourceCard);

                });

            } else if (sourcesContainer) {

                sourcesContainer.innerHTML = `

                    <div class="no-sources">
                        No source documents were returned.
                    </div>

                `;

            }


            // =================================================
            // SHOW ANSWER SECTION
            // =================================================

            if (answerSection) {

                answerSection.classList.remove("hidden");

                // Smooth scroll to answer

                setTimeout(() => {

                    answerSection.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }, 100);

            }


        } catch (error) {


            // =================================================
            // ERROR HANDLING
            // =================================================

            console.error("RAG Request Error:", error);


            if (answerSection) {

                answerSection.classList.remove("hidden");

            }


            if (answerText) {

                answerText.textContent =
                    "Unable to generate the legal answer. " +
                    error.message;

            }


            if (modelName) {

                modelName.textContent = "Error";

            }


            if (sourceCount) {

                sourceCount.textContent = "0 Sources";

            }

        } finally {


            // =================================================
            // RESET BUTTON
            // =================================================

            askButton.disabled = false;


            if (buttonText) {

                buttonText.textContent =
                    "ASK LEGAL QUESTION";

            }

        }

    }


    // =========================================================
    // BUTTON CLICK
    // =========================================================

    askButton.addEventListener(
        "click",
        askLegalQuestion
    );


    // =========================================================
    // CTRL + ENTER
    // =========================================================

    questionInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {

                event.preventDefault();

                askLegalQuestion();

            }

        }
    );


    // =========================================================
    // ESCAPE HTML
    // Prevent HTML injection inside source text
    // =========================================================

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent = value;

        return div.innerHTML;

    }


    console.log(
        "LegalRAG JavaScript loaded successfully."
    );

});