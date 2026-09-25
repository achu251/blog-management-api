const API_URL = "http://127.0.0.1:8000";

const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");


// LOGIN
loginForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    const formData = new URLSearchParams();

    formData.append("username", username);
    formData.append("password", password);

    try {

        const response = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            message.style.color = "red";
            message.textContent = data.detail || "Login failed";
            return;
        }

        localStorage.setItem("access_token", data.access_token);

        message.style.color = "green";
        message.textContent = "Login successful!";

        setTimeout(() => {
            window.location.href = "/static/dashboard.html";
        }, 800);

    } catch (error) {

        message.style.color = "red";
        message.textContent = "Unable to connect to server.";

        console.error(error);
    }
});


// SIGNUP
signupForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    const username = document.getElementById("signupUsername").value;
    const email = document.getElementById("signupEmail").value;
    const password = document.getElementById("signupPassword").value;

    const message = document.getElementById("signupMessage");

    try {

        const response = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            message.style.color = "red";
            message.textContent = data.detail || "Signup failed";
            return;
        }

        message.style.color = "green";
        message.textContent = "Account created successfully!";

        setTimeout(() => {
            showLogin();
        }, 1000);

    } catch (error) {

        message.style.color = "red";
        message.textContent = "Unable to connect to server.";

        console.error(error);
    }
});


// GOOGLE
function loginWithGoogle() {
    window.location.href = `${API_URL}/auth/google`;
}


// FACEBOOK
function loginWithFacebook() {
    window.location.href = `${API_URL}/auth/facebook`;
}


// SHOW SIGNUP
function showSignup() {

    document.getElementById("loginSection").style.display = "none";
    document.getElementById("signupSection").style.display = "block";
}


// SHOW LOGIN
function showLogin() {

    document.getElementById("signupSection").style.display = "none";
    document.getElementById("loginSection").style.display = "block";
}
