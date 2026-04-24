const BASE_URL = "http://127.0.0.1:8000";

async function calculate(operation) {
    const num1 = document.getElementById("num1").value;
    const num2 = document.getElementById("num2").value;
    const resultDiv = document.getElementById("result");

    if (!num1 || !num2) {
        resultDiv.innerText = "Please enter both numbers";
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}/${operation}?a=${num1}&b=${num2}`);
        const data = await response.json();

        if (!response.ok) {
            resultDiv.innerText = data.detail;
        } else {
            resultDiv.innerText = `Result: ${data.result}`;
        }
    } catch (error) {
        resultDiv.innerText = "Error connecting to backend";
    }
}