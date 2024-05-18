document.addEventListener('DOMContentLoaded', function() {
    // Function to change the greeting message
    function changeGreeting() {
        var newMessage = prompt('Enter a new greeting:');
        if (newMessage !== null && newMessage.trim() !== '') {
            alert('New greeting: ' + newMessage); // Just for demonstration
        }
    }

    // Event listener for the button click
    var changeButton = document.getElementById('changeButton');
    if (changeButton) {
        changeButton.addEventListener('click', changeGreeting);
    }

    // Function to display current time
    function displayCurrentTime() {
        var currentTime = new Date();
        var hours = currentTime.getHours();
        var minutes = currentTime.getMinutes();
        var seconds = currentTime.getSeconds();
        var timeString = hours + ':' + minutes + ':' + seconds;
        var currentTimeElement = document.getElementById('currentTime');
        if (currentTimeElement) {
            currentTimeElement.textContent = timeString;
        }
    }

    // Update time every second
    setInterval(displayCurrentTime, 1000);

    // Function to handle mouseover event
    function handleMouseOver(event) {
        event.target.style.backgroundColor = 'lightblue';
    }

    // Function to handle mouseout event
    function handleMouseOut(event) {
        event.target.style.backgroundColor = '';
    }

    // Add event listeners for mouseover and mouseout events
    var greetingElement = document.getElementById('greeting');
    if (greetingElement) {
        greetingElement.addEventListener('mouseover', handleMouseOver);
        greetingElement.addEventListener('mouseout', handleMouseOut);
    }
});
