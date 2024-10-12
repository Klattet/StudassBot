# Implementation of a virtual student assistant using large language models
## Goal
Research the effectiveness of- and develop a working prototype of a virtual student assistant and make it available to students for testing.

## Background
This project was created for Østfold University College as a bachelor's thesis in collaboration with @JegHeterTobias @khadijo @OmriJam . The project was chosen from a list of available projects via vote by the project collaborators. Østfold University College lent us a Jetson AGX Orin machine to help run our applications on, and we used it as a test platform for debugging and LLM testing.

The project did not only involve the implementation and testing of a prototype, but also research on how to create a persona to manipulate the language model to give responses in a certain way.

Multiple open source language models that were popular at the time were tested for their generation speed and the accuracy of their responses. We found that Llama2 by Meta and Orca2 by Microsoft had the best performance on our hardware, and we used Orca2 for the prototype.

The prototype was voluntarily alpha-tested by over 30 Programming-2 students at the campus, to varying degrees of success. We found that the quality of the LLM responses was highly dependent on the quality of the user's prompt. A common trend was that users initiated the conversation with a few or even a single word, leading to the generation of a poor or blank response. This meant that the effectiveness of the chatbot assistant was highly dependent on the user's prompting efficacy.

## Dependencies
- disnake
- haystack-ai
- jsonschema
- llama-cpp-haystack
- pdfminer.six
- python-docx
- websockets

```
pip install disnake haystack-ai jsonschema llama-cpp-haystack pdfminer.six python-docx websockets
```
or
```
pip install -r requirements.txt
```

**It can be a bit challenging to get llama_cpp to work depending on how you want to run the LLMs. You may need to build it with custom parameters.
See [here](https://github.com/abetlen/llama-cpp-python#supported-backends).**
