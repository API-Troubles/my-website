// Hi reader! Code is kinda scuffed lol :/

const imageOptions = {
  // Mapping from radio btn values to filepaths
  "image-none": null, // Nothing ):
  image1: "assets/flag-standalone.png",
  image2: "assets/flag-orpheus-left.png",
  image3: "assets/flag-orpheus-top.png",
  image4: "assets/flag-standalone-bw.png",
  image5: "assets/flag-orpheus-left-bw.png",
  image6: "assets/flag-orpheus-top-bw.png",
  image7: "assets/icon-progress-rounded.png",
  image8: "assets/icon-rounded.png",
  image9: "assets/nest.png",
};
const imageSizingOptions = {
  // Mapping from radio btn values to image size
  "image-none": null, // n/a
  image1: 0.6,
  image2: 0.6,
  image3: 0.6,
  image4: 0.6,
  image5: 0.6,
  image6: 0.6,
  image7: 0.8,
  image8: 0.8,
  image9: 0.7,
};
let qrCode = null;

function generateQRCode() {
  // Checks
  if (document.getElementById("url-field").value === "") {
    return; // If the url field is blank no qr code to generate ):
  }

  const dotsColor = document.getElementById("dots-color").value;

  // Get error correction level
  document.getElementById("qr-code").innerHTML = ""; // Clear any left over QR codes
  let errorCorLv = document.getElementById("error-correction").value;
  console.log(errorCorLv);

  // Show the download btns :)
  const div = document.querySelector(".download");
  const buttons = div.querySelectorAll("button");

  buttons.forEach((button) => {
    button.classList.remove("hidden");
  });

  // Get selected background image
  const radioImageOptions = document.querySelectorAll('.gallery input[name="image"]');

  let qrImage = null;
  let qrImageSizing = null;

  radioImageOptions.forEach((radioImageOption) => {
    if (radioImageOption.checked) {
      qrImage = imageOptions[radioImageOption.value];
      qrImageSizing = imageSizingOptions[radioImageOption.value];
    }
  });

  console.log(qrImage);

  qrCode = new QRCodeStyling({
    type: "svg",
    data: document.getElementById("url-field").value,
    qrOptions: {
      errorCorrectionLevel: errorCorLv,
    },
    dotsOptions: {
      color: dotsColor,
    },
    imageOptions: {
      imageSize: qrImageSizing,
      margin: 4,
    },
    image: qrImage,
  });

  qrCode.append(document.getElementById("qr-code"));
}

function downloadQRCode(type) {
  qrCode.download(type);
}
