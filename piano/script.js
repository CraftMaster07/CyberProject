// script.js

// Create a new Tone.js synth
const synth = new Tone.Synth().toDestination();

// Get all piano keys
const keys = document.querySelectorAll('.key');

// Add event listeners to all keys
keys.forEach(key => {
    key.addEventListener('click', () => {
        const note = key.getAttribute('data-note');
        synth.triggerAttackRelease(note, '8n');
    });
});
