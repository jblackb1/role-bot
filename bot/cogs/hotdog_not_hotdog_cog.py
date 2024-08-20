# hotdog_cog.py

import discord
from discord.ext import commands
from discord import app_commands
from keras.src.models import load_model
from keras.src.utils import load_img, img_to_array
import numpy as np
import os

class HotDogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Get the base directory and construct the path to the model file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, 'config')
        model_path = os.path.join(config_path, 'hotdog_not_hotdog_model.h5')
        
        # Load the model
        self.model = load_model(model_path)

    @app_commands.command(name="hotdog",
                          description="Attach an image and I will detect if it is hot dog or not hot dog.")
    async def hotdog(self, interaction: discord.Interaction, attachment: discord.Attachment):
        # Ensure an attachment was provided
        if not attachment:
            await interaction.response.send_message("Please attach an image.")
            return

        # Download the image
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_image.jpg')
        await attachment.save(img_path)

        # Preprocess the image
        img = load_img(img_path, target_size=(128, 128))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Predict
        prediction = self.model.predict(img_array)[0][0]

        # Interpret prediction
        if prediction > 0.5:
            result = "Hotdog"
        else:
            result = "Not hotdog."

        # Send the result back to the Discord channel
        await interaction.response.send_message(result)

        # Clean up the temporary image
        os.remove(img_path)

    async def download_image(self, url, file_path):
        async with self.bot.session.get(url) as response:
            if response.status == 200:
                with open(file_path, 'wb') as f:
                    f.write(await response.read())

def setup(bot):
    bot.add_cog(HotDogCog(bot))