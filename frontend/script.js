//allows javascript to find the buttons in html
//document is the HTML file loaded in the browser
const button = document.getElementById("shortenButton");
const input = document.getElementById("urlInput");
const result = document.getElementById("result");


//whenever the button is clicked, run this function
button.addEventListener("click", async () => {
    //fetch -> the broewser's way of making a request
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
    
    //window.location.origin = http://127.0.0.1:8000 in this case
    //changes the <p id="result"></p> html to <p id="result">...blabla url..</p>
    result.textContent = window.location.origin + "/" + data.shortened_url;
})