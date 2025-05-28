package com.example.myapplication;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.android.material.textfield.TextInputEditText;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class SignUp extends AppCompatActivity {
    FirebaseFirestore firestore;
    TextInputEditText nameInput, emailInput, usernameInput, passwordInput , numberInput;

    private static final int PERMISSION_REQUEST_CODE = 1;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_sign_up);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.activity_sign), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });
        firestore=FirebaseFirestore.getInstance();

        nameInput = findViewById(R.id.nameInput);
        usernameInput = findViewById(R.id.usernameInput);
        emailInput = findViewById(R.id.emailInput);
        numberInput = findViewById(R.id.phoneInput);
        passwordInput = findViewById(R.id.passwordInput);

        // Register Button Click Listener
        findViewById(R.id.login_button).setOnClickListener(view -> RegisterUser(view));
    }
    public class UserHelperClass {
        private String name;
        private String username;
        private String email;
        private String phone;
        private String password;

        // Constructor
        public UserHelperClass(String name, String username, String email, String phone, String password) {
            this.name = name;
            this.username = username;
            this.email = email;
            this.phone = phone;
            this.password = password;
        }

        // Getters and setters (optional but good practice)
        public String getName() {
            return name;
        }

        public String getUsername() {
            return username;
        }

        public String getEmail() {
            return email;
        }

        public String getPhone() {
            return phone;
        }

        public String getPassword() {
            return password;
        }

    }

    private Boolean validateName() {
        String val = nameInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            nameInput.setError("Field cannot be empty");
            return false;
        } else {
            nameInput.setError(null); // Remove any error
            return true;
        }
    }

    private Boolean validateUsername() {
        String val = usernameInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            usernameInput.setError("Username cannot be empty");
            return false;
        } else {
            usernameInput.setError(null); // Remove any error
            return true;
        }
    }

    private Boolean validateEmail() {
        String val = emailInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            emailInput.setError("Email cannot be empty");
            return false;
        } else {
            emailInput.setError(null); // Remove any error
            return true;
        }
    }

    private Boolean validatePhone() {
        String val = numberInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            numberInput.setError("Phone number cannot be empty");
            return false;
        } else {
            numberInput.setError(null); // Remove any error
            return true;
        }
    }

    private Boolean validatePassword() {
        String val = passwordInput.getText().toString(); // Get the text directly from TextInputEditText
        if (val.isEmpty()) {
            passwordInput.setError("Password cannot be empty");
            return false;
        } else {
            passwordInput.setError(null); // Remove any error
            return true;
        }
    }

    public void RegisterUser(View view) {
        String name = nameInput.getText().toString();
        String username = usernameInput.getText().toString();
        String email = emailInput.getText().toString();
        String phone = numberInput.getText().toString();
        String password = passwordInput.getText().toString();

        // Validate inputs before saving to Firebase
        if (validateName() && validateUsername() && validateEmail() && validatePhone() && validatePassword()) {
            // Create user data map
            Map<String, Object> userData = new HashMap<>();
            userData.put("name", name);
            userData.put("username", username);
            userData.put("email", email);
            userData.put("phone", phone);
            userData.put("password", password);  // Hash the password in a real app

            // Save data to Firestore
            firestore.collection("users")  // Firestore collection name
                    .document(email)  // Using email as the document ID
                    .set(userData)  // Save the userData map to Firestore
                    .addOnSuccessListener(aVoid -> {
                        // Data saved successfully
                        Toast.makeText(this, "User Registered!", Toast.LENGTH_SHORT).show();
                    })
                    .addOnFailureListener(e -> {
                        // Log the error
                        Log.e("RegisterUser", "Error saving user data to Firestore: " + e.getMessage());

                        // Provide user-friendly message
                        Toast.makeText(this, "Error: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                    });
        }
    }}