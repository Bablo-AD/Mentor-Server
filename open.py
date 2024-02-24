import openai

# Set up your OpenAI API key
openai.api_key = 'YOUR_API_KEY'

# Define your prompt
prompt = "Once upon a time"

# Generate text using OpenAI's GPT-3 model
response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=100
)

# Print the generated text
print(response.choices[0].text.strip())import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('My App'),
        ),
        body: Center(
          child: Text(
            'Start',
            style: TextStyle(fontSize: 24),
          ),
        ),
      ),
    );
  }
}