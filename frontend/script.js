//allows javascript to find the buttons in html
//document is the HTML file loaded in the browser
const button = document.getElementById("shortenButton");
const input = document.getElementById("urlInput");
const result = document.getElementById("result");


//whenever the button is clicked, run this function
//async function : allows you to wait for asynchronous operations
//await is only allowed in async functionsOk
button.addEventListener("click", async () => {
    //fetch -> the browser's way of making a request
    //normally, because http takes time, fetch returns a promise, but by using await, we wait for the actual result
    const response = await fetch("/shorten", {
        method : "POST",
        headers : {
            "Content-Type" : "application/json"
        },
        //turns the input value into a json text which can be sent over http
        body : JSON.stringify({
            url : input.value
        })
    });

    //takes the json response and converts it back into a JavaScript object
    const data = await response.json();

    //for debug
    // console.log("status:", response.status);
    // console.log("data:", data);

    //handle the case for too many requests
    //response.ok -> for successful responses in the 200-299 range
    if (!response.ok) {
        result.textContent = data.detail ?? "Something went wrong.";
        result.className = "error"; //makes a new class called error, so that the displayed text is red
        return;
    }
    
    
    //window.location.origin = http://127.0.0.1:8000 in this case
    //changes the <p id="result"></p> html to <p id="result">...blabla url..</p>
    //actually want a hyperlink instead of just text

    //Conceptually this adds:
    // <p id="result">
    //     <a href="http://127.0.0.1:8000/abc123">
    //         http://127.0.0.1:8000/abc123
    //     </a>
    // </p>

    const shortUrl = window.location.origin + "/" + data.shortened_url;
    result.innerHTML = ""; // clears everything currently inside the element

    const link = document.createElement("a");
    link.href = shortUrl;
    link.textContent = shortUrl;
    link.target = "_blank";  //makes link open in a new tab

    result.appendChild(link);
    result.className = "";   //clears the class for a successful response

})