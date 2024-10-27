// Fontawesome
// import "@fortawesome/fontawesome-free/scss/fontawesome.scss"
// import "@fortawesome/fontawesome-free/scss/solid.scss";
// import "@fortawesome/fontawesome-free/scss/regular.scss";
// import "@fortawesome/fontawesome-free/scss/v4-shims.scss";
import "@fortawesome/fontawesome-free/css/all.min.css";

import "startbootstrap-sb-admin-2/scss/sb-admin-2.scss";

import $ from "jquery";
import "bootstrap";
import "jquery-easing";

import "startbootstrap-sb-admin-2/js/sb-admin-2.js";

import "chart.js";
import "datatables.net-bs4";

import "select2";
import "select2/dist/css/select2.min.css";
import "@ttskch/select2-bootstrap4-theme/dist/select2-bootstrap4.min.css";

$(document).ready(function () {
  $(".select2").select2({
    theme: "bootstrap4",
    width: '100%',
  });
});

import "./css/styles.css";

// Your custom JavaScript code
$(document).ready(function () {
  console.log("Libs are ready!");
});
