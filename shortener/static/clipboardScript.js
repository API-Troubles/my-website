document.addEventListener("DOMContentLoaded", (event) => {
    console.log("DOM has fully loaded");
    document.querySelectorAll('.clipboard').forEach((clipboardSpan) => {
        clipboardSpan.addEventListener('click', () => {
            // Find the previous sibling element which is the adjacent <p> element
            const textToCopy = clipboardSpan.previousElementSibling.textContent;

            // Copy text to clipboard
            navigator.clipboard.writeText(textToCopy).then(() => {
                console.log('Text copied to clipboard: ' + textToCopy);
            }).catch((err) => {
                console.error('Failed to copy text: ', err);
            });
        });
    });
});