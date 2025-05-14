from together import Together

client = Together(api_key = "dc60eb96136cce98c635654556ef6c0f20738b926e6304a23e96778479dbd6dc")

imageCompletion = client.images.generate(
    model="black-forest-labs/FLUX.1-depth",
    width=1024,
    height=768,
    steps=28,
    prompt="show me this picture as a superhero",
    image_url="https://github.com/nutlope.png",
)

print(imageCompletion.data[0].url)