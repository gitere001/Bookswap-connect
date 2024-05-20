document.getElementById('signup-form').addEventListener('submit', function(event) {
	event.preventDefault();

	let first_name = document.getElementById('first_name').value;
	let last_name = document.getElementById('last_name').value;
	let email = document.getElementById('email').value;
	let password = document.getElementById('password').value;
	let confirm_password = document.getElementById('confirm_password').value;

	if (!first_name || !last_name || !email || !password || !confirm_password) {
		alert("All fields must be filled");
	    return;
	}

	if (password !== confirm_password) {
		alert("Passwords do not match");
		return;
	}
	console.log("Checking if email exists");
	fetch('/check_email', {
		method: 'POST',
		headers: {
			'Content-T': 'application/json'
		},
		body: JSON.stringify({ email: email })
	})
	.then(response => response.json())
	.then(data => {
		if (data.exists) {
			alert("Email already exists");
		} else {
			document.getElementById('signup-form').submit();
		}
	});
});