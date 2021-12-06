import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from sklearn.linear_model import LinearRegression

st.title("Yueer Liu's Final Project")
st.write("Student's name: Yueer Liu, ID: 51329186")
st.markdown("[Yueer Liu](https://github.com/YueerLiu) is a link to **Github**")
st.markdown("[Dataset](https://www.kaggle.com/attilakiss/secondhand-car-market-data-parsing-dataset-v1?select=advertisements_202006112147.csv) is a link to the dataset used in the project.")
st.write("The dataset originates from the biggest used car advertisement site of Hungary. It concludes every car's ID of advertisement, ID of region, Price of advertisement, Number of pictures ha benn uploaded to the advertisement, the type of proseller, the date of production, the brand and model, and so on.")
st.write("In this project, I will analyze the data from two perspectives: seller and buyer.")
st.write("The following is the whole data.")
df = pd.read_csv("C://Users//liuyu//Desktop//advertisements.csv",na_values=" ")
df

st.write("You can download the data by click the button.")

def convert_df(df):
     return df.to_csv().encode('utf-8')
csv = convert_df(df)
st.download_button(
     label="Download data as CSV",
     data=csv,
     file_name='advertisement of used car.csv',
     mime='text/csv'
 )


st.write("The whole date of production and uploaded date is not useful. I will seperate the date into year and month, then add colomns to the dataset.")
df["ProducedYear"]=df["production"].map(lambda x: x.split("-")[0])
df["UploadYear"]=df["upload_date"].map(lambda x: x.split("-")[0])
df["UploadMonth"]=df["upload_date"].map(lambda x: x.split("-")[1])
df[["ad_id","ProducedYear","UploadYear","UploadMonth"]]

st.header("Firstly, I'll analyze this data from the perspective of the seller who wants to advertise.")
st.subheader("What is the relationship between the price of advertisement and the number of pictures in the advertisement? Is it easier to sell if the advertisement is highlighted?")
a=alt.Chart(df.iloc[:5000]).mark_circle().encode(
    x = "ad_price",
    y = "numpictures",
    color = alt.Color('is_sold',scale=alt.Scale(scheme="turbo")),
    size="highlighted",
    tooltip = "ad_id"
)
c=alt.Chart(df.iloc[:5000]).mark_line().encode(
    x = "ad_price",
    y = "numpictures"
)
st.altair_chart(c+a)
st.write("There is no obvious relationship between the price of an AD and the number of images. Cheap ads can also show lots of photos. However, as you can see from the graph, the higher the advertising price, the number of images is not very small. Whether the car has already been sold or not, there are plenty of ads highlighted. It looks like most of the cars that were sold were highlighted.")
st.write("I will verify this relationship again computationally.")
numofsold=df["is_sold"].sum()
numofhighlightedinsold=(df["is_sold"]&df["highlighted"]).sum()
percentage=numofhighlightedinsold/numofsold
st.write(f"There are {numofsold} cars have been sold. In these sold cars, {numofhighlightedinsold} ads are highlighted. The percentage is **{percentage}**")
st.write("As it turns out, there was no clear correlation between whether the AD was highlighted and whether it was easier to sell a car.")


st.subheader("Will the brand of the car affect the price of advertising?")
st.write("Sellers can choose to see the average advertising price for the brand they want to know.")
st.write("The following is the number of each brand.")
dfbrand = pd.read_csv("C://Users//liuyu//Desktop//brand.csv")
dfbrand
numberbrand=st.number_input("Please input the number corresponding to the brand ", min_value=1, max_value=102)
mean=df[df["brand_id"]==numberbrand]["ad_price"].mean()
st.write(f"The mean price of the brand you choose is {mean}(in HUF).")


st.write("Perhaps, the different AD upload months will cause the different prices. BMW and Audi were used for the experiment.")
sub_df=df[(df["brand_id"]==8)| (df["brand_id"]==13) ]
sub_df["brand_id"]=sub_df["brand_id"].apply(str)
b=alt.Chart(sub_df[:5000]).mark_bar().encode(
    x='brand_id',
    y='ad_price',
    color='brand_id',
    column='UploadMonth'
)
st.altair_chart(b)
st.write("The blue bar chart is BMW, and the orange bar chart is Audi. As can be seen from the graph, there is an obvious relationship between advertising price and brand. Almost every month BMW's advertising price is higher than Audi's.")
st.write("At the same time, the figure clearly reflects that advertising prices are lower in summer and autumn, roughly from July to November.")


st.header("Second, I'll analyze this data from the perspective of the buyer.")
st.subheader("Search information")
st.write("When the buyer knows the ID of the advertisement, he can query all the information about the advertisement by the ID.")
SearchID=st.text_input("Please input the AD ID you want to search.", value=1545570)
st.table(df[df["ad_id"]==int(SearchID)])


st.subheader("Help buyers select the best vehicle.")
st.write("Buyers can specify personal capacity, number of doors, engine size and type of sale to find the most recommended model for a car that has not yet been sold.")
df1=df[~df["is_sold"]]
typeofseller = st.radio("choose the type of seller",('professional seller', 'private seller'))
if typeofseller=="professional seller":
    df2=df1[df1["proseller"]]
else:
    df2=df1[~df1["proseller"]]
doorsnumber= st.selectbox('How many doors do you want?',(2, 3, 4,5))
capacity=st.selectbox('How many personal capacity do you want?',(5,4,7,9,2,8,6,3,14,15,1,11,17,12))
energysize=st.slider("Choose the range of energy size",0,7538,(0,7538))
dt=df2["doorsnumber"]==doorsnumber
ct=df2["person_capacity"]==capacity
et=(df2["ccm"]>energysize[0]) & (df2["ccm"]<energysize[1])
df3=df2[dt&ct&et]

year=st.number_input("What is your minimum requirement for the year? The range of year is from 1900 to 2020",1900,2020)
st.write("The closer the year, the better. Highlight the number of year that meets the requirement. In the column of ProducedYear, the red numbers indicate compliance.")   
df3["ProducedYear"]=df3["ProducedYear"].astype(int)
def coloryear(y):
    is_max = (y>=year)
    return ['color : red' if v else '' for v in is_max]
result=df3[dt&ct&et].style.apply(coloryear,subset=['ProducedYear'])
result

st.write("Keep the miles as small as possible while meeting the buyer's requirements.  According to this request, recommend ten cars to buyers.")
df4=df3[df3["ProducedYear"]>=year]
df4=df4.sort_values("mileage",ascending=True)
df4[:10]
                     

st.header("Finally, Analyze the linear relationship between the advertisement price and mileage.")
d=alt.Chart(df).mark_circle().encode(
    x='mileage',
    y='ad_price'
)
st.altair_chart(d)
st.write("It is clear that there is a negative correlation between advertisement price and mileage.")
df5=df[:10000]
reg = LinearRegression()
X=np.array(df5["mileage"]).reshape(-1,1)
y=np.array(df5["ad_price"]).reshape(-1,1)
reg.fit(X,y)
coef=reg.coef_
intercept=reg.intercept_
st.write(f"The linear regression line's coefficient is {coef} and intercept is {intercept}")

st.subheader("Reference：")
st.markdown("A portion of the app is taken from [This link](https://docs.streamlit.io/library/api-reference/widgets/st.download_button) and [This link](https://www.kaggle.com/attilakiss/basic-statistical-data-visualization).")
