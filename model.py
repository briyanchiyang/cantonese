#!/usr/bin/env python

import flask
import torch

# Model packages
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, TrainingArguments
import numpy as np

# Audio recording packages
import sounddevice as sd
from scipy.io.wavfile import write

# Create application
APP = flask.Flask(__name__)

# Initialize model and processor
model = Wav2Vec2ForCTC.from_pretrained("briyanchiang/cantoclarity")
processor = Wav2Vec2Processor.from_pretrained("briyanchiang/cantoclarity")
print("e")

# All phoneme-related information for the sentence
class PhonemeWrapper:
  def __init__(self, phoneme, id, corresponding_id, accuracy):
    self.phoneme = phoneme
    self.id = id
    self.corresponding_id = corresponding_id
    self.accuracy = accuracy

  def print_all(self):
    print("Phoneme: ", self.phoneme, "\tId: ", self.id, "\tCorresponding id: ", self.corresponding_id, "\tAccuracy: ", self.accuracy)


def probability_analysis(ground_ids, input_ids, logits):
  ground_pointer = input_pointer = nonzero_entries = past_id = 0
  accuracies = [] # also store accuracy in an array so it can get passed + sent to HTML

  # Initialization of object
  ground_phonemes = []
  for id in ground_ids:
    phoneme_obj = PhonemeWrapper(processor.decode(id), id, None, None)
    ground_phonemes.append(phoneme_obj)

  while ground_pointer < len(ground_phonemes) and input_pointer < len(input_ids):

    # If match is found, we are done. Move to next ground_id
    if ground_phonemes[ground_pointer].id == input_ids[input_pointer]:

      ground_phonemes[ground_pointer].corresponding_id = past_id = input_pointer

      # Probability analysis
      sorted_probs = sorted(logits[0][input_pointer].tolist(), reverse=True)
      next_five_avg = sum(sorted_probs[1:6])/5
      ground_phonemes[ground_pointer].accuracy = round((1 - (next_five_avg / sorted_probs[0]))*100, 2)
      accuracies.append(ground_phonemes[ground_pointer].accuracy)

      print("Next five: ", next_five_avg, " , ", " High ", sorted_probs[0])

      # Next step
      ground_pointer += 1
      nonzero_entries = 0


    # If match is still not found by end of string, mark as unfound. "reset" input_pointer to prev char
    elif input_pointer == len(input_ids)-1:
      # print("Ground pointer is: ", ground_pointer ," and corresponding phoneme is ", ground_ids[ground_pointer])
      input_pointer = past_id
      ground_phonemes[ground_pointer].corresponding_id = -1
      ground_phonemes[ground_pointer].accuracy = 0
      accuracies.append(0)
      ground_pointer += 1

    # If there is a nonzero entry that isn't a match, record it
    elif input_ids[input_pointer] not in [211, 212, 213]:
      nonzero_entries += 1
    
    # Input_pointer still updates
    input_pointer += 1

  return ground_phonemes, accuracies

print("Starting")
# Render form
@APP.route('/')
def index():
  return flask.render_template('index.html')


@APP.route('/result', methods = ["POST", "GET"])
def result():
  return flask.render_template('index.html', name = "ffffff")



@APP.route('/handle_post', methods=['POST', 'GET'])
def handle_post():
    """ Displays the index page accessible at '/'
    """
    # Record audio
    freq = 16000
    duration = 3
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=1)
    sd.wait()

    # IDs of input recording
    recording = np.reshape(recording, -1)
    input_dict = processor(recording, return_tensors="pt", padding=True, sampling_rate=16000)
    logits = model(input_dict.input_values).logits
    pred_ids = torch.argmax(logits, dim=-1)[0]
    input_ids = pred_ids.tolist()

    # IDs of ground truth recording
    ground_phonemes = "nei5|ɡiuɜ|me1|minɡ4|aa1"
    with processor.as_target_processor():
        ground_ids = processor(ground_phonemes).input_ids

    print("Ground ids: ", ground_ids)
    print("Input ids: ", input_ids)

    # Mapping ground truth –> input + Probability analysis
    analysis, accuracies = probability_analysis(ground_ids, input_ids, logits)

    print("Accuracies: ", accuracies)

    # Getting input phonemes
    input_ids_new = []
    for i in input_ids:
      input_ids_new.append(i)
      input_ids_new.append(211) # space in between every phoneme

    input_phonemes = processor.decode(input_ids_new)

    for phoneme in analysis:
        phoneme.print_all()

    # Putting in appropriate format for HTML
    ground_phonemes = "n ei5 ɡ iuɜ m e1 m inɡ4 aa1"
    input_phonemes = input_phonemes.replace("|", " ")


    return flask.render_template('index.html', ground_phonemes = ground_phonemes, input_phonemes = input_phonemes, analysis = analysis)


if __name__ == '__main__':
    APP.debug=True
    APP.run(debug=True)

