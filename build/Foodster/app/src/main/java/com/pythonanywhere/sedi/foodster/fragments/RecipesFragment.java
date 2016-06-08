package com.pythonanywhere.sedi.foodster.fragments;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import com.pythonanywhere.sedi.foodster.R;
import com.pythonanywhere.sedi.foodster.models.JSONfunctions;
import com.pythonanywhere.sedi.foodster.models.ResponseWrapper;
import com.pythonanywhere.sedi.foodster.models.ShoppingList;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public class RecipesFragment extends Fragment {

    private static Spinner listSpinner;
    private static JSONArray jsonArray;

    private static String token;
    private static List<String> recipeNameList;
    private static List<ShoppingList> recipesList;

    public RecipesFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        SharedPreferences sharedPref
                = getActivity().getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
        token = sharedPref.getString(getString(R.string.saved_token), "");
//        updateSpinner();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        return inflater.inflate(R.layout.fragment_recipes, container, false);
    }

    public void updateSpinner(){
        if(listSpinner == null)
            new DownloadJSON().execute();
    }

    private class DownloadJSON extends AsyncTask<Void, Void, Void> {

        @Override
        protected Void doInBackground(Void... params) {

            recipeNameList = new ArrayList<String>();
            recipesList = new ArrayList<ShoppingList>();

            ResponseWrapper response = JSONfunctions.getWithJSONResult(getResources().getString(R.string.own_recipe_list), token);
            if(response.getResponseCode() == 200) {
                try {

                    System.out.println(response.getResponseCode());
                    jsonArray = response.getJSONArray();
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                JSONObject recipe;
                ShoppingList sl;
                JSONArray items;

                try {

                    for (int i = 0; i < jsonArray.length(); i++) {
                        recipe = jsonArray.getJSONObject(i);

                        recipeNameList.add(recipe.getString("name"));
                        sl = new ShoppingList(recipe.getString("name"),
                                recipe.getString("description"));

                        items = recipe.getJSONArray("items");
                        for (int j = 0; j < items.length(); j++) sl.addItem(items.getJSONObject(j));

                        recipesList.add(sl);


                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
            return null;
        }

        @Override
        protected void onPostExecute(Void args){

            listSpinner = (Spinner) getActivity().findViewById(R.id.spinner);
            listSpinner.setAdapter(new ArrayAdapter<String>(getActivity(),
                    android.R.layout.simple_spinner_item, recipeNameList));

            listSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
                @Override
                public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                    if(recipesList.get(position) != null) {
                        ShoppingItemsFragment itemFragment = new ShoppingItemsFragment();
                        itemFragment.setShoppingList(recipesList.get(position));
                        FragmentTransaction transaction = getChildFragmentManager().beginTransaction();
                        transaction.add(R.id.child_fragment, itemFragment).commit();
                    }
                }

                @Override
                public void onNothingSelected(AdapterView<?> parent) {

                }

            });

        }
    }
}
