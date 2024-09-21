import React, { useEffect, useState } from "react";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Heart } from "lucide-react";
import axios from 'axios';
const ARTICLES_API_URL = "http://localhost:5000/api/articles";
const RECOMMENDED_ARTICLES = "http://127.0.0.1:5000/api/articles/recommend"
const LIKES_API_URL = "http://localhost:5000/api/articles/like";


// const fetchArticles = async () => {
//   try {
//      let response = await axios.get(ARTICLES_API_URL);
//      let initialNews = response.data
//      console.log(response.data)
//      initialNews = initialNews.slice(0,20)
     
//   } catch (error) {
//     console.error("Error fetching articles:", error);
//   }
// };
// fetchArticles();


function Home() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true); // State to manage loading
    const [error, setError] = useState(null); // State to manage errors

    useEffect(() => {
        const fetchArticles = async () => {
            try {
                const response = await axios.get(ARTICLES_API_URL); // Replace with your API URL
                const res_rec = await axios.get(RECOMMENDED_ARTICLES); // Replace with your API URL
                if (res_rec.data != []) {
                    setNews(res_rec.data)
                }
                setNews(response.data.slice(0, 20)); // Get the first 20 articles
                console.log(news);
                
            } catch (err) {
                setError(err); // Handle error
            } finally {
                setLoading(false); // Set loading to false once the fetch is complete
            }

           
        };

        fetchArticles();
    }, [useState]);

    const handleLike = async (uid) => {
        try {
            
            setNews((prevNews) =>
                prevNews.map((article) =>
                    article.uid === uid ? { ...article, likes: (article.likes == 0)?1:0 } : article
                )
            );
            
            // Update the likes on the server
            await axios.post(`http://localhost:5000/api/articles/like/${uid}`, {uid}); 
            
            // Update the local state
        } catch (err) {
            console.error('Error liking article:', err);
            // Optionally handle error feedback to the user
        }
    };

    if (loading) {
        return <div>Loading articles...</div>;
    }

    // If there's an error, display an error message
    if (error) {
        return <div>Error fetching articles: {error.message}</div>;
    }

  return (
    <div>
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6">Buzz News</h1>
        <Input
          type="search"
          placeholder="Search news..."
          className="mb-6"
        //   value={}
        //   onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div className="">
            
          {news.map((article) => (
            <Card key={article.uid} className="flex flex-col m-10">
              <CardHeader>
                <CardTitle className="text-2xl text-start">{article.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex align-middle justify-around ">
                <img
                  src={article.image}
                  alt={article.title}
                  className="w-50 h-50 size-36 object-cover mb-4 rounded-md"
                />
                <p className="text-black text-start mt-4 w-[70%] text-xl">{article.summary}</p>
              </CardContent>
              <CardFooter className="flex justify-between items-center">
                <Button
                  variant="ghost"
                  size="sm"
                  className="flex items-center gap-2"
                  onClick={() => handleLike(article.uid)}
                >
                  <Heart className="h-4 w-4 " />
                  <span>{article.likes}</span>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;
